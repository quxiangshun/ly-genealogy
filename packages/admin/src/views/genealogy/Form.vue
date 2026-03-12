<template>
  <div class="genealogy-form">
    <el-form :model="form" label-width="120px" v-loading="loading">
      <el-form-item label="姓氏" required>
        <el-input v-model="form.surname" placeholder="如：屈" />
      </el-form-item>
      <el-form-item label="族谱名称" required>
        <el-input v-model="form.genealogy_name" placeholder="族谱名称" />
      </el-form-item>
      <el-form-item label="地区">
        <el-input v-model="form.region" placeholder="如：湖北秭归" />
      </el-form-item>
      <el-form-item label="年代">
        <el-input v-model="form.period" placeholder="如：清乾隆" />
      </el-form-item>
      <el-form-item label="卷数">
        <el-input v-model="form.volumes" placeholder="卷数" />
      </el-form-item>
      <el-form-item label="堂号">
        <el-input v-model="form.hall_name" placeholder="堂号" />
      </el-form-item>
      <el-form-item label="来源链接">
        <el-input v-model="form.source_url" placeholder="URL" />
      </el-form-item>
      <el-form-item label="始迁祖信息">
        <el-input v-model="form.founder_info" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="收藏信息">
        <el-input v-model="form.collection_info" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="散居地">
        <el-input v-model="form.scattered_region" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item label="简介">
        <el-input v-model="form.description" type="textarea" :rows="5" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submit" :loading="submitting">保存</el-button>
        <el-button @click="router.push('/genealogy')">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api/index'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string | undefined
const isEdit = !!id

const form = reactive({
  surname: '',
  genealogy_name: '',
  region: '',
  period: '',
  volumes: '',
  hall_name: '',
  source_url: '',
  founder_info: '',
  collection_info: '',
  scattered_region: '',
  description: '',
})

const loading = ref(false)
const submitting = ref(false)

async function fetchData() {
  if (!id) return
  loading.value = true
  try {
    const res = await api.get<Record<string, unknown>>(`/genealogies/${id}`)
    const d = res.data
    if (d) {
      form.surname = String(d.surname ?? '')
      form.genealogy_name = String(d.genealogy_name ?? '')
      form.region = String(d.region ?? '')
      form.period = String(d.period ?? '')
      form.volumes = String(d.volumes ?? '')
      form.hall_name = String(d.hall_name ?? '')
      form.source_url = String(d.source_url ?? '')
      form.founder_info = String(d.founder_info ?? '')
      form.collection_info = String(d.collection_info ?? '')
      form.scattered_region = String(d.scattered_region ?? '')
      form.description = String(d.description ?? '')
    }
  } catch (e) {
    ElMessage.error('加载失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!form.surname || !form.genealogy_name) {
    ElMessage.warning('请填写姓氏和族谱名称')
    return
  }
  submitting.value = true
  try {
    if (isEdit) {
      await api.put(`/genealogies/${id}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/genealogies', form)
      ElMessage.success('创建成功')
    }
    router.push('/genealogy')
  } catch (e) {
    ElMessage.error('保存失败')
    console.error(e)
  } finally {
    submitting.value = false
  }
}

watch(() => route.params.id, fetchData, { immediate: true })
onMounted(fetchData)
</script>

<style scoped>
.genealogy-form { padding: 20px; max-width: 700px; }
</style>
