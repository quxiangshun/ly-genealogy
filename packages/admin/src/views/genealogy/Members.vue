<template>
  <div class="members-page">
    <div class="toolbar">
      <el-button type="primary" @click="router.push(`/member/add?genealogyId=${genealogyId}`)">新增成员</el-button>
      <el-button @click="router.push(`/genealogy/${genealogyId}/edit`)">返回族谱</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="gender" label="性别" width="80">
        <template #default="{ row }">{{ row.gender === 'F' ? '女' : '男' }}</template>
      </el-table-column>
      <el-table-column prop="generation_number" label="世系" width="80" />
      <el-table-column prop="courtesy_name" label="字/号" width="120" />
      <el-table-column prop="birth_date" label="出生" width="100" />
      <el-table-column prop="death_date" label="卒年" width="100" />
      <el-table-column label="父亲">
        <template #default="{ row }">{{ getFatherName(row.father_id) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="router.push(`/member/${row.id}`)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../../api/index'

const route = useRoute()
const router = useRouter()
const genealogyId = route.params.id as string

const list = ref<Record<string, unknown>[]>([])
const loading = ref(false)
const fatherMap = ref<Record<number, string>>({})

async function fetchList() {
  if (!genealogyId) return
  loading.value = true
  try {
    const res = await api.get<Record<string, unknown>[]>(`/members?genealogy_id=${genealogyId}`)
    list.value = res.data ?? []
    fatherMap.value = {}
    for (const m of list.value) {
      const fid = m.father_id as number | undefined
      if (fid) {
        const f = list.value.find((x) => x.id === fid)
        if (f) fatherMap.value[fid] = String(f.name ?? '')
      }
    }
  } catch (e) {
    ElMessage.error('加载失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

function getFatherName(fatherId: unknown): string {
  if (fatherId == null) return ''
  return fatherMap.value[Number(fatherId)] ?? ''
}

function handleDelete(row: Record<string, unknown>) {
  ElMessageBox.confirm('确定要删除该成员吗？', '确认删除', {
    type: 'warning',
  }).then(async () => {
    try {
      await api.delete(`/members/${row.id}`)
      ElMessage.success('删除成功')
      fetchList()
    } catch (e) {
      ElMessage.error('删除失败')
      console.error(e)
    }
  }).catch(() => {})
}

watch(() => route.params.id, fetchList, { immediate: true })
onMounted(fetchList)
</script>

<style scoped>
.members-page { padding: 20px; }
.toolbar { margin-bottom: 16px; }
</style>
