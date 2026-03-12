<template>
  <div>
    <div class="text-center mb-4">
      <p class="heritage-subtitle mb-3">屈氏百科</p>
      <h1 class="display-5 mb-2" style="letter-spacing: 0.08em">屈氏百科</h1>
      <p class="lead text-muted mb-0">屈氏家族历史文化知识库</p>
      <HeritageDivider />
    </div>

    <div class="wiki-search-bar mb-4">
      <form @submit.prevent="doSearch" class="input-group">
        <input
          v-model="searchQ"
          type="text"
          class="form-control"
          placeholder="搜索百科词条..."
        />
        <button type="submit" class="btn btn-primary">
          <i class="bi bi-search"></i>
        </button>
      </form>
    </div>

    <div class="wiki-cat-tabs mb-4">
      <NuxtLink
        v-for="cat in wikiCategories"
        :key="cat"
        :to="buildWikiUrl(cat)"
        class="wiki-cat-tab"
        :class="{ active: currentCat === cat }"
      >
        {{ catLabel(cat) }}
        <span class="wiki-cat-count">({{ cat === '' ? total : (catCounts[cat] ?? 0) }})</span>
      </NuxtLink>
    </div>

    <div class="row">
      <div class="col-lg-9">
        <StatBanner
          v-if="totalViews !== undefined"
          :items="[{ value: totalViews, unit: '次', label: '累计浏览' }]"
        />
        <div class="row g-3">
          <div
            v-for="item in items"
            :key="item.id"
            class="col-md-6 col-lg-4"
          >
            <NuxtLink :to="`/wiki/${item.slug}`" class="wiki-card-link">
              <div class="card heritage-card h-100 wiki-card">
                <div class="card-body d-flex flex-column">
                  <div class="mb-2">
                    <span class="wiki-card-cat">{{ catLabel(item.category) }}</span>
                    <span v-if="item.era" class="wiki-card-era ms-1">{{ item.era }}</span>
                  </div>
                  <h6 class="wiki-card-title">{{ item.title }}</h6>
                  <p v-if="item.summary" class="wiki-card-summary">{{ item.summary }}</p>
                  <div class="wiki-card-footer small text-muted">
                    <i class="bi bi-eye me-1"></i>{{ item.view_count ?? 0 }} 次浏览
                  </div>
                </div>
              </div>
            </NuxtLink>
          </div>
        </div>
        <nav v-if="pages > 1" class="mt-4 d-flex justify-content-center">
          <ul class="pagination">
            <li class="page-item" :class="{ disabled: page <= 1 }">
              <NuxtLink
                :to="buildWikiUrl(currentCat, page - 1)"
                class="page-link"
              >
                上一页
              </NuxtLink>
            </li>
            <li class="page-item" :class="{ disabled: page >= pages }">
              <NuxtLink
                :to="buildWikiUrl(currentCat, page + 1)"
                class="page-link"
              >
                下一页
              </NuxtLink>
            </li>
          </ul>
        </nav>
      </div>
      <div class="col-lg-3">
        <div class="card heritage-card mb-4">
          <div class="card-header">热门词条</div>
          <div class="card-body p-0">
            <HotList
              :items="hotEntries"
              base-url="/wiki"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const config = useRuntimeConfig()
const route = useRoute()

const CAT_LABELS: Record<string, string> = {
  '': '全部',
  origin: '起源',
  celebrity: '名人',
  hall: '堂号',
  custom: '习俗',
  relic: '遗迹',
  other: '其他',
}

const currentCat = computed(() => (route.query.cat as string) || '')
const searchQ = ref((route.query.q as string) || '')
const page = computed(() => Math.max(1, parseInt(String(route.query.page ?? 1), 10)))

watch(() => route.query.q, (q) => { searchQ.value = q || '' })

const { data: wikiData } = useFetch(
  () => {
    const params = new URLSearchParams()
    if (currentCat.value) params.set('cat', currentCat.value)
    if (searchQ.value) params.set('q', searchQ.value)
    params.set('page', String(page.value))
    return `${config.public.apiBase}/api/wiki?${params}`
  },
  {
    key: () => `wiki-list-${currentCat.value}-${searchQ.value}-${page.value}`,
  }
)

const items = computed(() => wikiData.value?.items ?? [])
const total = computed(() => wikiData.value?.total ?? 0)
const pages = computed(() => wikiData.value?.pages ?? 1)
const catCounts = computed(() => wikiData.value?.catCounts ?? {})
const hotEntries = computed(() => {
  const h = wikiData.value?.hotEntries ?? []
  return h.map((e: { slug: string; title: string; view_count?: number }) => ({
    slug: e.slug,
    title: e.title,
    viewCount: e.view_count,
  }))
})
const totalViews = computed(() => wikiData.value?.totalViews ?? 0)

const wikiCategories = ['', 'origin', 'celebrity', 'hall', 'custom', 'relic', 'other']

function catLabel(cat: string) {
  return (CAT_LABELS[cat] ?? cat) || '全部'
}

function buildWikiUrl(cat: string, p?: number) {
  const q: Record<string, string> = {}
  if (cat) q.cat = cat
  if (searchQ.value) q.q = searchQ.value
  if (p && p > 1) q.page = String(p)
  const qs = new URLSearchParams(q).toString()
  return qs ? `/wiki?${qs}` : '/wiki'
}

function doSearch() {
  navigateTo(buildWikiUrl(currentCat.value))
}
</script>
