<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="8" :md="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <span class="stat-value">{{ stats.genealogyCount ?? '-' }}</span>
            <span class="stat-label">族谱数</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <span class="stat-value">{{ stats.memberCount ?? '-' }}</span>
            <span class="stat-label">成员数</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <span class="stat-value">{{ stats.generationCount ?? '-' }}</span>
            <span class="stat-label">字辈数</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <span class="stat-value">{{ stats.wikiCount ?? '-' }}</span>
            <span class="stat-label">百科词条</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <span class="stat-value">{{ stats.newsCount ?? '-' }}</span>
            <span class="stat-label">新闻动态</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :md="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近族谱</span>
              <el-button type="primary" link @click="$router.push('/genealogy')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentGenealogies" stripe>
            <el-table-column prop="surname" label="姓氏" width="70" />
            <el-table-column prop="name" label="族谱名称" show-overflow-tooltip />
            <el-table-column prop="region" label="地区" width="100" show-overflow-tooltip />
            <el-table-column prop="memberCount" label="成员" width="70" align="center" />
            <el-table-column prop="createdAt" label="创建时间" width="170" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="$router.push(`/genealogy/${row.id}/edit`)">
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近新闻</span>
              <el-button type="primary" link @click="$router.push('/news')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentNews" stripe>
            <el-table-column prop="title" label="标题" show-overflow-tooltip />
            <el-table-column prop="createdAt" label="发布时间" width="170" />
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="$router.push(`/news/${row.id}/edit`)">
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '../api/index'

interface Stats {
  genealogyCount?: number
  memberCount?: number
  generationCount?: number
  wikiCount?: number
  newsCount?: number
}

interface RecentGenealogy {
  id: number
  surname: string
  name: string
  region: string
  memberCount: number
  createdAt: string
}

interface RecentNews {
  id: number
  title: string
  category: string
  createdAt: string
}

interface StatsResponse extends Stats {
  recentGenealogies?: RecentGenealogy[]
  recentNews?: RecentNews[]
}

const stats = ref<Stats>({})
const recentGenealogies = ref<RecentGenealogy[]>([])
const recentNews = ref<RecentNews[]>([])

onMounted(async () => {
  try {
    const res = await api.get<StatsResponse>('/stats')
    stats.value = res.data
    recentGenealogies.value = res.data.recentGenealogies ?? []
    recentNews.value = res.data.recentNews ?? []
  } catch {
    // leave defaults
  }
})
</script>

<style scoped>
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 20px;
  border-left: 3px solid var(--admin-gold);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-family: var(--font-title);
  font-size: 28px;
  font-weight: 700;
  color: var(--admin-accent);
}

.stat-label {
  font-family: var(--font-title);
  font-size: 14px;
  color: var(--admin-ink-muted);
}

.content-row {
  margin-top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
