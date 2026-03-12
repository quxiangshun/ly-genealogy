<template>
  <div>
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><NuxtLink to="/">首页</NuxtLink></li>
        <li class="breadcrumb-item"><NuxtLink to="/wiki">百科</NuxtLink></li>
        <li class="breadcrumb-item active" aria-current="page">{{ entry?.title || '加载中...' }}</li>
      </ol>
    </nav>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <template v-else-if="entry">
      <div class="wiki-article-header mb-4">
        <h1 class="wiki-article-title">{{ entry.title }}</h1>
        <div class="wiki-article-meta mt-2">
          <span v-if="entry.category">{{ catLabel(entry.category) }}</span>
          <span v-if="entry.era">{{ entry.era }}</span>
          <span>创建：{{ formatTime(entry.create_time) }}</span>
          <span>更新：{{ formatTime(entry.update_time) }}</span>
          <span><i class="bi bi-eye me-1"></i>{{ entry.view_count ?? 0 }} 次浏览</span>
        </div>
      </div>
      <div
        class="wiki-article-body"
        v-html="renderedContent"
      />
      <div v-if="relatedEntries.length > 0" class="mt-5">
        <h5 class="mb-3">相关词条</h5>
        <ul class="list-group">
          <li
            v-for="r in relatedEntries"
            :key="r.slug"
            class="list-group-item list-group-item-action"
          >
            <NuxtLink :to="`/wiki/${r.slug}`">{{ r.title }}</NuxtLink>
          </li>
        </ul>
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

const { data: entry, error } = useFetch(
  () => `${config.public.apiBase}/api/wiki/${slug.value}`,
  {
    key: () => `wiki-${slug.value}`,
  }
)

const renderedContent = computed(() => {
  const c = entry.value?.content
  if (!c) return ''
  return marked(c) as string
})

const relatedEntries = computed(() => {
  const e = entry.value
  if (!e) return []
  return []
})

function catLabel(cat: string) {
  return CAT_LABELS[cat] ?? cat
}

function formatTime(t: string | undefined) {
  if (!t) return '—'
  return t.slice(0, 10)
}
</script>
