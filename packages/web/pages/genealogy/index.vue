<template>
  <div>
    <h2 class="border-bottom mb-3">族谱库</h2>
    <p class="lead text-muted mb-4">检索屈氏族谱，按姓氏、地区、年代浏览</p>

    <!-- Search/Filter form -->
    <form class="row g-2 g-md-3 mb-4" @submit.prevent="applyFilters">
      <div class="col-4 col-md-3">
        <label class="form-label">姓氏</label>
        <input
          v-model="filters.surname"
          type="text"
          class="form-control"
          inputmode="text"
          placeholder="如：屈"
        >
      </div>
      <div class="col-4 col-md-3">
        <label class="form-label">地区</label>
        <select v-model="filters.region" class="form-select">
          <option value="">全部</option>
          <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>
      <div class="col-4 col-md-3">
        <label class="form-label">年代</label>
        <input
          v-model="filters.period"
          type="text"
          class="form-control"
          inputmode="text"
          placeholder="如：清"
        >
      </div>
      <div class="col-12 col-md-3 d-flex align-items-end gap-2">
        <button type="submit" class="btn btn-primary flex-grow-1 flex-md-grow-0">
          <i class="bi bi-search me-1" />检索
        </button>
        <button type="button" class="btn btn-outline-secondary" @click="resetFilters">
          重置
        </button>
      </div>
    </form>

    <!-- Genealogy grid -->
    <div v-if="pending" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger heritage-alert">
      {{ error.message || '加载失败' }}
    </div>
    <div v-else-if="!genealogies?.length" class="alert alert-info heritage-alert">
      暂无族谱数据
    </div>
    <div v-else class="row g-3">
      <div
        v-for="g in genealogies"
        :key="g.id"
        class="col-md-6 col-lg-4"
      >
        <NuxtLink :to="`/genealogy/${g.id}`" class="text-decoration-none">
          <div class="card heritage-card h-100">
            <div class="card-body">
              <h5 class="card-title">
                {{ g.genealogy_name }}
                <span v-if="g.hall_name" class="genealogy-hall-badge">{{ g.hall_name }}</span>
              </h5>
              <p class="card-text small text-muted mb-1">
                {{ g.surname }} · {{ g.region || '—' }} · {{ g.period || '—' }}
              </p>
              <p class="card-text small mb-0">
                <i class="bi bi-people me-1" />{{ g.member_count ?? 0 }} 人
              </p>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string
const route = useRoute()

const filters = reactive({
  surname: (route.query.surname as string) || '',
  region: (route.query.region as string) || '',
  period: '',
})

const { data: stats } = useLazyFetch<{ regions: string[] }>(`${apiBase}/api/stats`, {
  key: 'stats-regions',
  server: false,
})
const regions = computed(() => stats.value?.regions ?? [])

const fetchKey = ref(0)
const {
  data: genealogies,
  pending,
  error,
} = useLazyFetch<Array<Record<string, unknown>>>(
  () => {
    const params = new URLSearchParams()
    if (filters.surname) params.set('surname', filters.surname)
    if (filters.region) params.set('region', filters.region)
    if (filters.period) params.set('period', filters.period)
    const qs = params.toString()
    return `${apiBase}/api/genealogies${qs ? '?' + qs : ''}`
  },
  { key: () => `genealogies-${fetchKey.value}`, server: false },
)

function applyFilters() {
  fetchKey.value++
}

function resetFilters() {
  filters.surname = ''
  filters.region = ''
  filters.period = ''
  fetchKey.value++
}

useHead({
  title: '族谱库 - 屈氏宗谱',
  meta: [
    {
      name: 'description',
      content: '检索屈氏族谱，按姓氏、地区、年代浏览族谱信息。',
    },
  ],
})
</script>
