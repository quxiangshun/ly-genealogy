<template>
  <div class="news-list">
    <div class="toolbar">
      <el-button type="primary" @click="router.push('/news/add')">新增资讯</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column prop="event_date" label="事件日期" width="120" />
      <el-table-column prop="is_published" label="发布" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_published ? 'success' : 'info'" size="small">
            {{ row.is_published ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_pinned" label="置顶" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_pinned" type="warning" size="small">置顶</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" label="浏览量" width="90" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="router.push(`/news/${row.id}/edit`)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="fetchList"
      class="mt-3"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../../api/index'

const router = useRouter()
const list = ref<Record<string, unknown>[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get<{ items: Record<string, unknown>[]; total: number }>(`/news?page=${page.value}`)
    list.value = res.data?.items ?? []
    total.value = res.data?.total ?? 0
  } catch (e) {
    ElMessage.error('加载失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

function handleDelete(row: Record<string, unknown>) {
  ElMessageBox.confirm('确定要删除该资讯吗？', '确认删除', {
    type: 'warning',
  }).then(async () => {
    try {
      await api.delete(`/news/${row.id}`)
      ElMessage.success('删除成功')
      fetchList()
    } catch (e) {
      ElMessage.error('删除失败')
      console.error(e)
    }
  }).catch(() => {})
}

watch(page, fetchList)
onMounted(fetchList)
</script>

<style scoped>
.news-list { padding: 20px; }
.toolbar { margin-bottom: 16px; }
.mt-3 { margin-top: 16px; }
</style>
