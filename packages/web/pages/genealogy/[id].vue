<template>
  <div>
    <nav aria-label="breadcrumb" class="mb-3">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><NuxtLink to="/genealogy"><i class="bi bi-book me-1"></i>族谱库</NuxtLink></li>
        <li class="breadcrumb-item active" aria-current="page">{{ genealogy?.genealogy_name || '加载中...' }}</li>
      </ol>
    </nav>

    <div v-if="error" class="alert alert-danger heritage-alert">加载失败</div>

    <template v-else-if="genealogy">
      <!-- Title -->
      <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-4">
        <div>
          <h2 class="mb-1">{{ genealogy.genealogy_name }}</h2>
          <div class="d-flex flex-wrap gap-2 align-items-center">
            <span class="badge" style="background:rgba(176,138,80,0.15);color:var(--heritage-accent);font-size:0.85rem">{{ genealogy.surname }}氏</span>
            <span v-if="genealogy.hall_name" class="badge" style="background:rgba(92,107,74,0.12);color:#4a5c3a;font-size:0.85rem">{{ genealogy.hall_name }}</span>
            <span v-if="genealogy.region" class="text-muted small"><i class="bi bi-geo-alt me-1"></i>{{ genealogy.region }}</span>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Left: Info -->
        <div class="col-lg-8">
          <div class="card heritage-card mb-4">
            <div class="card-header"><i class="bi bi-journal-richtext me-2"></i>谱籍信息</div>
            <div class="card-body">
              <dl class="row mb-0">
                <template v-if="genealogy.region">
                  <dt class="col-sm-3"><i class="bi bi-geo-alt me-1 text-muted"></i>地区</dt>
                  <dd class="col-sm-9">{{ genealogy.region }}</dd>
                </template>
                <template v-if="genealogy.period">
                  <dt class="col-sm-3"><i class="bi bi-clock-history me-1 text-muted"></i>年代/刊本</dt>
                  <dd class="col-sm-9">{{ genealogy.period }}</dd>
                </template>
                <template v-if="genealogy.volumes">
                  <dt class="col-sm-3"><i class="bi bi-journal-text me-1 text-muted"></i>卷数</dt>
                  <dd class="col-sm-9">{{ genealogy.volumes }}</dd>
                </template>
                <template v-if="genealogy.hall_name">
                  <dt class="col-sm-3"><i class="bi bi-house-door me-1 text-muted"></i>堂号</dt>
                  <dd class="col-sm-9">{{ genealogy.hall_name }}</dd>
                </template>
                <template v-if="genealogy.scattered_region">
                  <dt class="col-sm-3"><i class="bi bi-pin-map me-1 text-muted"></i>散居地</dt>
                  <dd class="col-sm-9">{{ genealogy.scattered_region }}</dd>
                </template>
                <template v-if="genealogy.collection_info">
                  <dt class="col-sm-3"><i class="bi bi-building me-1 text-muted"></i>馆藏信息</dt>
                  <dd class="col-sm-9">{{ genealogy.collection_info }}</dd>
                </template>
              </dl>
              <template v-if="genealogy.founder_info">
                <hr>
                <div class="mb-0">
                  <strong><i class="bi bi-person-lines-fill me-1"></i>始祖/世系源流：</strong>
                  <div class="heritage-quote" style="margin:0.5rem 0 0 0">{{ genealogy.founder_info }}</div>
                </div>
              </template>
              <template v-if="genealogy.description">
                <hr>
                <div class="heritage-quote" style="margin:0">{{ genealogy.description }}</div>
              </template>
              <template v-if="genealogy.source_url">
                <hr>
                <p class="mb-0">
                  <i class="bi bi-link-45deg me-1"></i><strong>参考链接：</strong>
                  <a v-if="genealogy.source_url.startsWith('http')" :href="genealogy.source_url" target="_blank" rel="noopener">
                    在线查阅 <i class="bi bi-box-arrow-up-right"></i>
                  </a>
                  <span v-else class="text-muted">{{ genealogy.source_url }}</span>
                </p>
              </template>
            </div>
          </div>
        </div>

        <!-- Right: Stats + Generations -->
        <div class="col-lg-4">
          <div v-if="genealogy.member_count != null" class="card heritage-card mb-4">
            <div class="card-header"><i class="bi bi-bar-chart me-2"></i>统计</div>
            <div class="card-body">
              <div class="d-flex justify-content-around text-center">
                <div>
                  <div style="font-size:1.6rem;font-weight:700;color:var(--heritage-accent)">{{ genealogy.member_count ?? 0 }}</div>
                  <div class="small text-muted">已录成员</div>
                </div>
                <div>
                  <div style="font-size:1.6rem;font-weight:700;color:var(--heritage-red)">{{ generations?.length ?? 0 }}</div>
                  <div class="small text-muted">字辈</div>
                </div>
              </div>
            </div>
          </div>
          <div v-if="generations?.length" class="card heritage-card mb-4">
            <div class="card-header"><i class="bi bi-list-ol me-2"></i>字辈摘要</div>
            <div class="card-body">
              <p class="mb-0" style="letter-spacing:0.15em;line-height:2">
                <span v-for="gen in generations" :key="gen.id" class="me-1" style="font-size:1.05rem">{{ gen.character }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const route = useRoute()
const id = computed(() => route.params.id as string)

const { data: genealogy, error } = useLazyFetch<Record<string, unknown>>(
  () => `${config.public.apiBase}/api/genealogies/${id.value}`,
  { key: () => `genealogy-${id.value}` }
)

const { data: generations } = useLazyFetch<Array<{ id: number; character: string; sort_order: number; note?: string }>>(
  () => `${config.public.apiBase}/api/generations/${id.value}`,
  { key: () => `genealogy-gens-${id.value}` }
)

useHead({
  title: computed(() => genealogy.value ? `${genealogy.value.genealogy_name} - 屈氏宗谱` : '族谱详情 - 屈氏宗谱'),
})
</script>
