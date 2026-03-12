<template>
  <div class="member-query">
    <el-form :inline="true" class="search-form">
      <el-form-item label="族谱">
        <el-select v-model="genealogyId" placeholder="全部" clearable filterable style="width: 240px">
          <el-option v-for="g in genealogies" :key="g.id" :label="`${g.surname} - ${g.genealogy_name}`" :value="g.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="姓名">
        <el-input v-model="name" placeholder="输入姓名搜索" clearable style="width: 180px" @keyup.enter="search" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="search">搜索</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="results" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="gender" label="性别" width="80">
        <template #default="{ row }">{{ row.gender === 'F' ? '女' : '男' }}</template>
      </el-table-column>
      <el-table-column prop="generation_number" label="世系" width="80" />
      <el-table-column prop="genealogy_name" label="族谱" min-width="150" />
      <el-table-column prop="birth_date" label="出生" width="100" />
      <el-table-column prop="death_date" label="卒年" width="100" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="router.push(`/member/${row.id}`)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api/index'

const router = useRouter()
const genealogies = ref<Record<string, unknown>[]>([])
const genealogyId = ref<number | null>(null)
const name = ref('')
const results = ref<Record<string, unknown>[]>([])
const loading = ref(false)

async function fetchGenealogies() {
  try {
    const res = await api.get<Record<string, unknown>[]>('/genealogies')
    genealogies.value = res.data ?? []
  } catch (e) {
    console.error(e)
  }
}

async function search() {
  if (!name.value.trim()) {
    ElMessage.warning('请输入姓名')
    return
  }
  loading.value = true
  try {
    let url = `/query/search?name=${encodeURIComponent(name.value.trim())}`
    if (genealogyId.value) url += `&genealogy_id=${genealogyId.value}`
    const res = await api.get<Record<string, unknown>[]>(url)
    results.value = res.data ?? []
  } catch (e) {
    ElMessage.error('搜索失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchGenealogies)
</script>

<style scoped>
.member-query { padding: 20px; }
.search-form { margin-bottom: 16px; }
</style>
