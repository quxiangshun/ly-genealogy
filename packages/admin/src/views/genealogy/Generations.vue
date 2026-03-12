<template>
  <div class="generations-page">
    <div class="toolbar">
      <el-button type="primary" @click="addRow">新增字辈</el-button>
      <el-button @click="router.push(`/genealogy/${genealogyId}`)" v-if="genealogyId">返回族谱</el-button>
    </div>
    <el-table :data="generations" v-loading="loading">
      <el-table-column type="index" label="#" width="60" />
      <el-table-column label="字辈" width="120">
        <template #default="{ row }">
          <el-input v-model="row.character" placeholder="字辈" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="备注">
        <template #default="{ row }">
          <el-input v-model="row.note" placeholder="备注" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ $index }">
          <el-button link type="primary" size="small" @click="moveUp($index)" :disabled="$index === 0">上移</el-button>
          <el-button link type="primary" size="small" @click="moveDown($index)" :disabled="$index === generations.length - 1">下移</el-button>
          <el-button link type="danger" size="small" @click="removeRow($index)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="save-bar">
      <el-button type="primary" @click="save" :loading="saving">保存</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api/index'

const route = useRoute()
const router = useRouter()
const genealogyId = route.params.id as string

interface GenRow {
  character: string
  note: string
}

const generations = ref<GenRow[]>([])
const loading = ref(false)
const saving = ref(false)

async function fetchData() {
  if (!genealogyId) return
  loading.value = true
  try {
    const res = await api.get<Record<string, unknown>[]>(`/generations/${genealogyId}`)
    generations.value = (res.data ?? []).map((g) => ({
      character: String(g.character ?? ''),
      note: String(g.note ?? ''),
    }))
  } catch (e) {
    ElMessage.error('加载失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

function addRow() {
  generations.value.push({ character: '', note: '' })
}

function removeRow(index: number) {
  generations.value.splice(index, 1)
}

function moveUp(index: number) {
  if (index <= 0) return
  const arr = generations.value
  ;[arr[index - 1], arr[index]] = [arr[index], arr[index - 1]]
}

function moveDown(index: number) {
  if (index >= generations.value.length - 1) return
  const arr = generations.value
  ;[arr[index], arr[index + 1]] = [arr[index + 1], arr[index]]
}

async function save() {
  saving.value = true
  try {
    await api.put(`/generations/${genealogyId}`, {
      generations: generations.value.map((g) => ({ character: g.character, note: g.note })),
    })
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
    console.error(e)
  } finally {
    saving.value = false
  }
}

watch(() => route.params.id, fetchData, { immediate: true })
onMounted(fetchData)
</script>

<style scoped>
.generations-page { padding: 20px; }
.toolbar { margin-bottom: 16px; }
.save-bar { margin-top: 16px; }
</style>
