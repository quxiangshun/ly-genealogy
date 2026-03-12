<template>
  <div>
    <div class="text-center mb-4">
      <p class="heritage-subtitle mb-3">辈字检索 · 寻根溯源</p>
      <h1 class="display-5 mb-2" style="letter-spacing: 0.08em">字辈查询</h1>
      <p class="lead text-muted mb-0">输入您名字中的辈字，匹配所属族谱</p>
      <HeritageDivider />
    </div>

    <div class="zibei-search-box">
      <form class="zibei-form" @submit.prevent="submitSearch">
        <div class="input-group input-group-lg">
          <span class="input-group-text"><i class="bi bi-search"></i></span>
          <input
            v-model="keyword"
            type="text"
            class="form-control form-control-lg"
            placeholder="输入辈字（如：昌、德、永）"
            autocomplete="off"
          />
          <button type="submit" class="btn btn-primary">查询</button>
        </div>
      </form>
    </div>

    <div v-if="pending" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>

    <div v-else-if="(resultsList?.length ?? 0) > 0" class="row g-3">
      <div
        v-for="(entry, idx) in resultsList"
        :key="idx"
        class="col-md-6 col-lg-4"
      >
        <div class="card heritage-card h-100 zibei-result-card">
          <div class="card-body">
            <h6 class="card-title text-primary mb-2">
              {{ genealogyDisplayName(entry.genealogy) }}
            </h6>
            <p v-if="(entry.genealogy as { region?: string })?.region" class="small text-muted mb-2">
              {{ (entry.genealogy as { region?: string })?.region }}
            </p>
            <div class="zibei-chars">
              <span
                v-for="(gen, gi) in (entry.generations as { character: string; sort_order: number; note?: string }[])"
                :key="gi"
                class="zibei-char"
                :class="{
                  'zibei-char-match': keyword && (gen.character as string).includes(keyword),
                }"
                :title="`第${gen.sort_order + 1}世${gen.note ? ' - ' + gen.note : ''}`"
              >
                {{ gen.character }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="hasSearched && keyword.trim()" class="text-center py-4 text-muted">
      <p class="mb-0">未找到包含「{{ keyword }}」的族谱字辈</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const config = useRuntimeConfig()
const route = useRoute()

const keyword = ref((route.query.q as string) || '')
const hasSearched = ref(false)
const fetchKey = ref(0)

const { data: results, pending } = useLazyFetch<ZibeiEntry[]>(
  () => {
    const q = keyword.value.trim()
    const params = q ? `?q=${encodeURIComponent(q)}` : ''
    return `${config.public.apiBase}/api/culture/zibei${params}`
  },
  {
    key: () => `zibei-${fetchKey.value}`,
    server: false,
  },
)

interface ZibeiGenealogy {
  genealogy_name?: string
  surname?: string
  region?: string
}

interface ZibeiEntry {
  genealogy: ZibeiGenealogy
  generations: { character: string; sort_order: number; note?: string }[]
}

const resultsList = computed(() => {
  const r = results.value
  return Array.isArray(r) ? r : []
})

function genealogyDisplayName(g: ZibeiGenealogy) {
  return g?.genealogy_name || `${g?.surname || ''}${g?.region || ''}` || '族谱'
}

function submitSearch() {
  hasSearched.value = true
  fetchKey.value++
}
</script>
