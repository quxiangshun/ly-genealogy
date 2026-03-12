<template>
  <div>
    <div class="text-center mb-4">
      <p class="heritage-subtitle mb-3">亲缘关系 · 世系传承</p>
      <h1 class="display-5 mb-2" style="letter-spacing: 0.08em">亲缘查询</h1>
      <p class="lead text-muted mb-0">查询同一族谱内两人的亲缘关系</p>
      <HeritageDivider />
    </div>

    <div class="rel-search-box">
      <form @submit.prevent="submitForm" autocomplete="off">
        <div class="row g-3">
          <div class="col-12">
            <label class="form-label">选择族谱</label>
            <select v-model="form.genealogy_id" class="form-select" required>
              <option value="">请选择族谱</option>
              <option
                v-for="g in genealogies"
                :key="g.id"
                :value="g.id"
              >
                {{ g.genealogy_name }}（{{ g.region || '—' }}）
              </option>
            </select>
          </div>
          <div class="col-12 col-md-5">
            <label class="form-label">成员 A</label>
            <div class="position-relative">
              <input
                v-model="form.name_a"
                type="text"
                class="form-control"
                inputmode="text"
                enterkeyhint="next"
                placeholder="输入姓名"
                autocomplete="off"
                required
                @focus="showAcA = true"
                @blur="onBlurA"
                @input="form.id_a = null; onInputA()"
              />
              <div
                v-show="showAcA && acItemsA.length > 0"
                class="rel-autocomplete"
              >
                <div
                  v-for="item in acItemsA"
                  :key="item.id"
                  class="rel-ac-item"
                  @mousedown.prevent="selectAcA(item)"
                  @touchend.prevent="selectAcA(item)"
                >
                  {{ item.display || item.name }}
                </div>
              </div>
            </div>
          </div>
          <div class="col-12 col-md-2 d-flex align-items-center justify-content-center py-1 py-md-3">
            <span class="rel-vs"><i class="bi bi-arrow-left-right d-none d-md-inline"></i><i class="bi bi-arrow-down d-md-none"></i></span>
          </div>
          <div class="col-12 col-md-5">
            <label class="form-label">成员 B</label>
            <div class="position-relative">
              <input
                v-model="form.name_b"
                type="text"
                class="form-control"
                inputmode="text"
                enterkeyhint="search"
                placeholder="输入姓名"
                autocomplete="off"
                required
                @focus="showAcB = true"
                @blur="onBlurB"
                @input="form.id_b = null; onInputB()"
              />
              <div
                v-show="showAcB && acItemsB.length > 0"
                class="rel-autocomplete"
              >
                <div
                  v-for="item in acItemsB"
                  :key="item.id"
                  class="rel-ac-item"
                  @mousedown.prevent="selectAcB(item)"
                  @touchend.prevent="selectAcB(item)"
                >
                  {{ item.display || item.name }}
                </div>
              </div>
            </div>
          </div>
          <div class="col-12">
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? '查询中...' : '查询关系' }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- Disambiguation -->
    <div v-if="result?.disambiguate" class="rel-disambiguate card heritage-card p-4 mb-4">
      <h6 class="mb-3">存在重名，请选择具体成员</h6>
      <form @submit.prevent="submitDisambiguate">
        <div v-if="result.members_a" class="mb-3">
          <label class="form-label">成员 A（{{ form.name_a }}）</label>
          <div class="form-check" v-for="m in result.members_a" :key="m.id">
            <input
              v-model="form.id_a"
              type="radio"
              name="id_a"
              :value="m.id"
              class="form-check-input"
            />
            <label class="form-check-label">
              {{ m.name }}（第{{ m.generation_number || '?' }}世）
            </label>
          </div>
        </div>
        <div v-if="result.members_b" class="mb-3">
          <label class="form-label">成员 B（{{ form.name_b }}）</label>
          <div class="form-check" v-for="m in result.members_b" :key="m.id">
            <input
              v-model="form.id_b"
              type="radio"
              name="id_b"
              :value="m.id"
              class="form-check-input"
            />
            <label class="form-check-label">
              {{ m.name }}（第{{ m.generation_number || '?' }}世）
            </label>
          </div>
        </div>
        <button type="submit" class="btn btn-primary">确认查询</button>
      </form>
    </div>

    <!-- Result -->
    <div v-else-if="result && !result.disambiguate && !result.error" class="rel-result card heritage-card p-4">
      <div class="rel-result-label">{{ result.relation }}</div>
      <div class="rel-path-visual mt-4">
        <div class="rel-path-title mb-3"><i class="bi bi-diagram-3 me-1"></i>传承路径</div>
        <div class="rel-chain">
          <template v-for="(m, i) in (result.chain_a || [])" :key="'a-' + m.id">
            <div
              class="rel-node"
              :class="{
                'rel-node-lca': i === 0,
                'rel-node-self': i === (result.chain_a?.length ?? 0) - 1,
              }"
            >
              <span class="rel-node-name">{{ m.name }}</span>
              <span v-if="(m as { generation_number?: number })?.generation_number" class="rel-node-gen">
                第{{ (m as { generation_number?: number }).generation_number }}世
              </span>
            </div>
            <div v-if="i < (result.chain_a?.length ?? 0) - 1" class="rel-arrow">
              <i class="bi bi-arrow-down"></i>
            </div>
          </template>
        </div>
        <div class="rel-arrow"><i class="bi bi-arrow-down"></i></div>
        <div class="rel-chain">
          <template v-for="(m, i) in (result.chain_b || [])" :key="'b-' + m.id">
            <div
              class="rel-node"
              :class="{ 'rel-node-self': i === (result.chain_b?.length ?? 0) - 1 }"
            >
              <span class="rel-node-name">{{ m.name }}</span>
              <span v-if="(m as { generation_number?: number })?.generation_number" class="rel-node-gen">
                第{{ (m as { generation_number?: number }).generation_number }}世
              </span>
            </div>
            <div v-if="i < (result.chain_b?.length ?? 0) - 1" class="rel-arrow">
              <i class="bi bi-arrow-down"></i>
            </div>
          </template>
        </div>
      </div>
    </div>

    <div v-else-if="result?.error" class="alert alert-warning heritage-alert">
      {{ result.error }}
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const config = useRuntimeConfig()

interface Genealogy {
  id: number
  genealogy_name: string
  region?: string
}

interface AcItem {
  id: number
  name: string
  display?: string
  generation?: number
  father?: string
}

interface RelResult {
  relation?: string
  chain_a?: { id: number; name: string; generation_number?: number }[]
  chain_b?: { id: number; name: string; generation_number?: number }[]
  disambiguate?: boolean
  members_a?: { id: number; name: string; generation_number?: number }[]
  members_b?: { id: number; name: string; generation_number?: number }[]
  error?: string
}

const { data: genealogies } = useFetch<Genealogy[]>(
  () => `${config.public.apiBase}/api/genealogies`,
  { key: 'rel-genealogies' }
)

const form = reactive({
  genealogy_id: '' as number | '',
  name_a: '',
  name_b: '',
  id_a: null as number | null,
  id_b: null as number | null,
})

const showAcA = ref(false)
const showAcB = ref(false)
const acItemsA = ref<AcItem[]>([])
const acItemsB = ref<AcItem[]>([])
const acTimerA = ref<ReturnType<typeof setTimeout> | null>(null)
const acTimerB = ref<ReturnType<typeof setTimeout> | null>(null)
const submitting = ref(false)
const result = ref<RelResult | null>(null)

async function fetchAutocomplete(field: 'a' | 'b', q: string) {
  if (!form.genealogy_id || !q.trim()) return []
  const url = `${config.public.apiBase}/api/query/autocomplete?genealogy_id=${form.genealogy_id}&q=${encodeURIComponent(q)}`
  const data = await $fetch<AcItem[]>(url)
  return data || []
}

function onInputA() {
  if (acTimerA.value) clearTimeout(acTimerA.value)
  acTimerA.value = setTimeout(async () => {
    acItemsA.value = await fetchAutocomplete('a', form.name_a)
    acTimerA.value = null
  }, 200)
}

function onInputB() {
  if (acTimerB.value) clearTimeout(acTimerB.value)
  acTimerB.value = setTimeout(async () => {
    acItemsB.value = await fetchAutocomplete('b', form.name_b)
    acTimerB.value = null
  }, 200)
}

function onBlurA() {
  setTimeout(() => { showAcA.value = false }, 150)
}

function onBlurB() {
  setTimeout(() => { showAcB.value = false }, 150)
}

function selectAcA(item: AcItem) {
  form.name_a = item.name
  form.id_a = item.id
  showAcA.value = false
  acItemsA.value = []
}

function selectAcB(item: AcItem) {
  form.name_b = item.name
  form.id_b = item.id
  showAcB.value = false
  acItemsB.value = []
}

async function doSubmit() {
  result.value = null
  submitting.value = true
  try {
    const res = await $fetch<RelResult>(`${config.public.apiBase}/api/culture/relationship`, {
      method: 'POST',
      body: {
        genealogy_id: Number(form.genealogy_id),
        name_a: form.name_a.trim(),
        name_b: form.name_b.trim(),
        id_a: form.id_a || undefined,
        id_b: form.id_b || undefined,
      },
    })
    result.value = res
  } catch (e) {
    result.value = { error: '请求失败，请稍后重试' }
  } finally {
    submitting.value = false
  }
}

function submitForm() {
  doSubmit()
}

function submitDisambiguate() {
  doSubmit()
}
</script>
