<template>
  <div class="genealogy-list">
    <div class="toolbar">
      <el-button type="primary" @click="router.push('/genealogy/add')">新增族谱</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="surname" label="姓氏" width="100" />
      <el-table-column prop="genealogy_name" label="族谱名称" min-width="150" />
      <el-table-column prop="region" label="地区" width="120" />
      <el-table-column prop="period" label="年代" width="120" />
      <el-table-column prop="hall_name" label="堂号" width="120" />
      <el-table-column prop="member_count" label="成员数" width="90" />
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="router.push(`/genealogy/${row.id}/edit`)">编辑</el-button>
          <el-button link type="primary" @click="router.push(`/admin/genealogy/${row.id}/generations`)">字辈</el-button>
          <el-button link type="primary" @click="router.push(`/genealogy/${row.id}/members`)">成员</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../../api/index'

const router = useRouter()
const list = ref<Record<string, unknown>[]>([])
const loading = ref(false)

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get<Record<string, unknown>[]>('/genealogies')
    list.value = res.data ?? []
  } catch (e) {
    ElMessage.error('加载失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

function handleDelete(row: Record<string, unknown>) {
  ElMessageBox.confirm('确定要删除该族谱吗？', '确认删除', {
    type: 'warning',
  }).then(async () => {
    try {
      await api.delete(`/genealogies/${row.id}`)
      ElMessage.success('删除成功')
      fetchList()
    } catch (e) {
      ElMessage.error('删除失败')
      console.error(e)
    }
  }).catch(() => {})
}

onMounted(fetchList)
</script>

<style scoped>
.genealogy-list { padding: 20px; }
.toolbar { margin-bottom: 16px; }
</style>
