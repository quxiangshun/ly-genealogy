export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string
  const baseUrl = getRequestURL(event).origin

  const urls: string[] = [
    `${baseUrl}/`,
    `${baseUrl}/genealogy`,
    `${baseUrl}/culture`,
    `${baseUrl}/culture/zibei`,
    `${baseUrl}/culture/relationship`,
    `${baseUrl}/culture/contact`,
    `${baseUrl}/wiki`,
    `${baseUrl}/news`,
  ]

  try {
    const genealogies = await $fetch<Array<{ id: number }>>(`${apiBase}/api/genealogies`).catch(() => [])
    for (const g of genealogies) {
      urls.push(`${baseUrl}/genealogy/${g.id}`)
    }

    const wikiFirst = await $fetch<{ items: Array<{ slug: string }>; pages: number }>(`${apiBase}/api/wiki`).catch(() => ({ items: [], pages: 1 }))
    const wikiItems = [...wikiFirst.items]
    if (wikiFirst.pages > 1) {
      const wikiRest = await Promise.all(
        Array.from({ length: wikiFirst.pages - 1 }, (_, i) =>
          $fetch<{ items: Array<{ slug: string }> }>(`${apiBase}/api/wiki?page=${i + 2}`).catch(() => ({ items: [] }))
        )
      )
      for (const r of wikiRest) wikiItems.push(...r.items)
    }
    for (const w of wikiItems) {
      urls.push(`${baseUrl}/wiki/${w.slug}`)
    }

    const newsFirst = await $fetch<{ items: Array<{ slug: string }>; pages: number }>(`${apiBase}/api/news`).catch(() => ({ items: [], pages: 1 }))
    const newsItems = [...newsFirst.items]
    if (newsFirst.pages > 1) {
      const newsRest = await Promise.all(
        Array.from({ length: newsFirst.pages - 1 }, (_, i) =>
          $fetch<{ items: Array<{ slug: string }> }>(`${apiBase}/api/news?page=${i + 2}`).catch(() => ({ items: [] }))
        )
      )
      for (const r of newsRest) newsItems.push(...r.items)
    }
    for (const n of newsItems) {
      urls.push(`${baseUrl}/news/${n.slug}`)
    }
  } catch (err) {
    console.error('Sitemap fetch error:', err)
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map((u) => `  <url><loc>${escapeXml(u)}</loc></url>`).join('\n')}
</urlset>`

  setHeader(event, 'Content-Type', 'application/xml')
  setHeader(event, 'Cache-Control', 'public, max-age=3600')
  return xml
})

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}
