<template>
  <div>
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><NuxtLink to="/">首页</NuxtLink></li>
        <li class="breadcrumb-item"><NuxtLink to="/news">动态</NuxtLink></li>
        <li class="breadcrumb-item active" aria-current="page">{{ article?.title || '加载中...' }}</li>
      </ol>
    </nav>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <template v-else-if="article">
      <div class="wiki-article-header mb-4">
        <h1 class="wiki-article-title">{{ article.title }}</h1>
        <div class="wiki-article-meta mt-2">
          <span v-if="article.category">{{ catLabel(article.category) }}</span>
          <span>{{ formatTime(article.create_time) }}</span>
          <span v-if="article.source">来源：{{ article.source }}</span>
          <span><i class="bi bi-eye me-1"></i>{{ article.view_count ?? 0 }} 次浏览</span>
        </div>
      </div>
      <div
        class="wiki-article-body"
        v-html="renderedContent"
      />
      <div class="d-flex justify-content-between mt-5 pt-4 border-top">
        <NuxtLink
          v-if="article.prev_slug"
          :to="`/news/${article.prev_slug}`"
          class="news-nav-link"
        >
          <span class="small text-muted">上一篇</span>
          <span><i class="bi bi-arrow-left me-1"></i>上一篇</span>
        </NuxtLink>
        <span v-else></span>
        <NuxtLink
          v-if="article.next_slug"
          :to="`/news/${article.next_slug}`"
          class="news-nav-link text-end"
        >
          <span class="small text-muted">下一篇</span>
          <span>下一篇<i class="bi bi-arrow-right ms-1"></i></span>
        </NuxtLink>
        <span v-else></span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'

definePageMeta({
  layout: 'default',
})

const config = useRuntimeConfig()
const route = useRoute()
const slug = computed(() => route.params.slug as string)

const CAT_LABELS: Record<string, string> = {
  origin: '起源',
  celebrity: '名人',
  hall: '堂号',
  custom: '习俗',
  relic: '遗迹',
  other: '其他',
}

const { data: article, error } = useFetch(
  () => `${config.public.apiBase}/api/news/${slug.value}`,
  {
    key: () => `news-${slug.value}`,
  }
)

const renderedContent = computed(() => {
  const c = article.value?.content
  if (!c) return ''
  return marked(c) as string
})

function catLabel(cat: string) {
  return CAT_LABELS[cat] ?? cat
}

function formatTime(t: string | undefined) {
  if (!t) return '—'
  return t.slice(0, 16).replace('T', ' ')
}
</script>
