<template>
  <div>
    <div class="text-center mb-4">
      <p class="heritage-subtitle mb-3">屈氏动态</p>
      <h1 class="display-5 mb-2" style="letter-spacing: 0.08em">新闻动态</h1>
      <p class="lead text-muted mb-0">屈氏家族最新资讯</p>
      <HeritageDivider />
    </div>

    <div class="wiki-search-bar mb-4">
      <form @submit.prevent="doSearch" class="input-group">
        <input
          v-model="searchQ"
          type="text"
          class="form-control"
          placeholder="搜索新闻..."
        />
        <button type="submit" class="btn btn-primary">
          <i class="bi bi-search"></i>
        </button>
      </form>
    </div>

    <div class="wiki-cat-tabs mb-4">
      <NuxtLink
        v-for="cat in newsCategories"
        :key="cat"
        :to="buildNewsUrl(cat)"
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
        <div class="news-list">
          <NuxtLink
            v-for="item in items"
            :key="item.id"
            :to="`/news/${item.slug}`"
            class="news-list-item"
            :class="{ 'news-pinned': item.is_pinned }"
          >
            <div class="news-list-date">
              <span class="news-date-main">{{ formatDate(item.create_time) }}</span>
              <span class="news-date-year">{{ formatYear(item.create_time) }}</span>
            </div>
            <div class="news-list-body">
              <span v-if="item.category" class="news-list-cat me-2">{{ catLabel(item.category) }}</span>
              <span v-if="item.is_pinned" class="badge bg-danger me-2">置顶</span>
              <div class="news-list-title">{{ item.title }}</div>
              <div v-if="item.summary" class="news-list-summary">{{ item.summary }}</div>
            </div>
            <div class="news-list-arrow"><i class="bi bi-chevron-right"></i></div>
          </NuxtLink>
        </div>
        <nav v-if="pages > 1" class="mt-4 d-flex justify-content-center">
          <ul class="pagination">
            <li class="page-item" :class="{ disabled: page <= 1 }">
              <NuxtLink
                :to="buildNewsUrl(currentCat, page - 1)"
                class="page-link"
              >
                上一页
              </NuxtLink>
            </li>
            <li class="page-item" :class="{ disabled: page >= pages }">
              <NuxtLink
                :to="buildNewsUrl(currentCat, page + 1)"
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
          <div class="card-header">热门文章</div>
          <div class="card-body p-0">
            <HotList
              :items="hotArticles"
              base-url="/news"
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

const newsCategories = ['', 'origin', 'celebrity', 'hall', 'custom', 'relic', 'other']

watch(() => route.query.q, (q) => { searchQ.value = q || '' })

const { data: newsData } = useFetch(
  () => {
    const params = new URLSearchParams()
    if (currentCat.value) params.set('cat', currentCat.value)
    if (searchQ.value) params.set('q', searchQ.value)
    params.set('page', String(page.value))
    return `${config.public.apiBase}/api/news?${params}`
  },
  {
    key: () => `news-list-${currentCat.value}-${searchQ.value}-${page.value}`,
  }
)

const items = computed(() => newsData.value?.items ?? [])
const total = computed(() => newsData.value?.total ?? 0)
const pages = computed(() => newsData.value?.pages ?? 1)
const catCounts = computed(() => newsData.value?.catCounts ?? {})
const hotArticles = computed(() => {
  const h = newsData.value?.hotArticles ?? []
  return h.map((a: { slug: string; title: string; view_count?: number }) => ({
    slug: a.slug,
    title: a.title,
    viewCount: a.view_count,
  }))
})
const totalViews = computed(() => newsData.value?.totalViews ?? 0)

function catLabel(cat: string) {
  return (CAT_LABELS[cat] ?? cat) || '全部'
}

function buildNewsUrl(cat: string, p?: number) {
  const q: Record<string, string> = {}
  if (cat) q.cat = cat
  if (searchQ.value) q.q = searchQ.value
  if (p && p > 1) q.page = String(p)
  const qs = new URLSearchParams(q).toString()
  return qs ? `/news?${qs}` : '/news'
}

function doSearch() {
  navigateTo(buildNewsUrl(currentCat.value))
}

function formatDate(t: string | undefined) {
  if (!t) return '—'
  const d = t.slice(0, 10).split('-')
  return d.length >= 3 ? `${d[1]}-${d[2]}` : t
}

function formatYear(t: string | undefined) {
  if (!t) return ''
  return t.slice(0, 4)
}
</script>
