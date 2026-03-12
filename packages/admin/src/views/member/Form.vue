<template>
  <div class="member-form">
    <el-form :model="form" label-width="120px" v-loading="loading">
      <el-form-item label="所属族谱" required v-if="!genealogyId">
        <el-select v-model="form.genealogy_id" placeholder="请选择族谱" filterable style="width: 100%">
          <el-option v-for="g in genealogies" :key="g.id" :label="`${g.surname} - ${g.genealogy_name}`" :value="g.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="姓名" required>
        <el-input v-model="form.name" placeholder="姓名" />
      </el-form-item>
      <el-form-item label="性别">
        <el-select v-model="form.gender" placeholder="性别" style="width: 120px">
          <el-option label="男" value="M" />
          <el-option label="女" value="F" />
        </el-select>
      </el-form-item>
      <el-form-item label="世系">
        <el-input-number v-model="form.generation_number" :min="1" placeholder="世系" />
      </el-form-item>
      <el-form-item label="字/号">
        <el-input v-model="form.courtesy_name" placeholder="字或号" />
      </el-form-item>
      <el-form-item label="出生日期">
        <el-input v-model="form.birth_date" placeholder="如：清乾隆十年" />
      </el-form-item>
      <el-form-item label="卒年">
        <el-input v-model="form.death_date" placeholder="如：道光五年" />
      </el-form-item>
      <el-form-item label="出生地">
        <el-input v-model="form.birth_place" placeholder="出生地" />
      </el-form-item>
      <el-form-item label="父亲">
        <el-select
          v-model="form.father_id"
          filterable
          remote
          :remote-method="(q: string) => searchMembers(q, 'father')"
          :loading="fatherLoading"
          placeholder="搜索父亲"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="m in fatherOptions"
            :key="m.id"
            :label="m.display || `${m.name}（第${m.generation ?? '?'}世）`"
            :value="m.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="母亲">
        <el-select
          v-model="form.mother_id"
          filterable
          remote
          :remote-method="(q: string) => searchMembers(q, 'mother')"
          :loading="motherLoading"
          placeholder="搜索母亲"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="m in motherOptions"
            :key="m.id"
            :label="m.display || `${m.name}（第${m.generation ?? '?'}世）`"
            :value="m.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="配偶">
        <el-input v-model="form.spouse_name" placeholder="配偶姓名" />
      </el-form-item>
      <el-form-item label="照片">
        <el-upload
          :action="uploadUrl"
          :headers="uploadHeaders"
          name="file"
          :show-file-list="false"
          :on-success="onUploadSuccess"
          :before-upload="beforeUpload"
        >
          <el-button size="small" type="primary">上传图片</el-button>
        </el-upload>
        <el-input v-model="form.photo" placeholder="或输入图片URL" class="mt-2" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.notes" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submit" :loading="submitting">保存</el-button>
        <el-button @click="goBack">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api/index'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string | undefined
const isEdit = !!id

const genealogyId = computed(() => {
  const q = route.query.genealogyId as string | undefined
  if (q) return q
  return form.genealogy_id ? String(form.genealogy_id) : ''
})

const uploadUrl = '/api/upload'
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('admin_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

interface AutocompleteItem {
  id: number
  name: string
  generation: number | null
  father: string
  display?: string
}

const form = reactive({
  genealogy_id: null as number | null,
  name: '',
  gender: 'M' as 'M' | 'F',
  generation_number: null as number | null,
  courtesy_name: '',
  birth_date: '',
  death_date: '',
  birth_place: '',
  father_id: null as number | null,
  mother_id: null as number | null,
  spouse_name: '',
  photo: '',
  notes: '',
})

const genealogies = ref<Record<string, unknown>[]>([])
const fatherOptions = ref<AutocompleteItem[]>([])
const motherOptions = ref<AutocompleteItem[]>([])
const fatherLoading = ref(false)
const motherLoading = ref(false)
const loading = ref(false)
const submitting = ref(false)

async function fetchGenealogies() {
  try {
    const res = await api.get<Record<string, unknown>[]>('/genealogies')
    genealogies.value = res.data ?? []
  } catch (e) {
    console.error(e)
  }
}

async function searchMembers(q: string, type: 'father' | 'mother') {
  const gid = form.genealogy_id ?? (route.query.genealogyId ? Number(route.query.genealogyId) : null)
  if (!gid) {
    if (type === 'father') fatherOptions.value = []
    else motherOptions.value = []
    return
  }
  if (type === 'father') fatherLoading.value = true
  else motherLoading.value = true
  try {
    const res = await api.get<AutocompleteItem[]>(`/query/autocomplete?genealogy_id=${gid}&q=${encodeURIComponent(q || ' ')}`)
    const items = res.data ?? []
    if (type === 'father') fatherOptions.value = items
    else motherOptions.value = items
  } catch (e) {
    if (type === 'father') fatherOptions.value = []
    else motherOptions.value = []
  } finally {
    if (type === 'father') fatherLoading.value = false
    else motherLoading.value = false
  }
}

function beforeUpload() {
  return true
}

function onUploadSuccess(res: { url?: string }) {
  form.photo = res?.url ?? ''
}

async function fetchData() {
  if (!id) {
    const q = route.query.genealogyId as string | undefined
    if (q) form.genealogy_id = parseInt(q, 10)
    return
  }
  loading.value = true
  try {
    const res = await api.get<Record<string, unknown>>(`/members/${id}`)
    const d = res.data
    if (d) {
      form.genealogy_id = Number(d.genealogy_id)
      form.name = String(d.name ?? '')
      form.gender = (d.gender === 'F' ? 'F' : 'M') as 'M' | 'F'
      form.generation_number = d.generation_number != null ? Number(d.generation_number) : null
      form.courtesy_name = String(d.courtesy_name ?? '')
      form.birth_date = String(d.birth_date ?? '')
      form.death_date = String(d.death_date ?? '')
      form.birth_place = String(d.birth_place ?? '')
      form.father_id = d.father_id != null ? Number(d.father_id) : null
      form.mother_id = d.mother_id != null ? Number(d.mother_id) : null
      form.spouse_name = String(d.spouse_name ?? '')
      form.photo = String(d.photo ?? '')
      form.notes = String(d.notes ?? '')
    }
  } catch (e) {
    ElMessage.error('加载失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function submit() {
  const gid = form.genealogy_id ?? (route.query.genealogyId ? Number(route.query.genealogyId) : null)
  if (!gid && !isEdit) {
    ElMessage.warning('请选择族谱')
    return
  }
  if (!form.name) {
    ElMessage.warning('请填写姓名')
    return
  }
  submitting.value = true
  try {
    const payload = {
      name: form.name,
      gender: form.gender,
      generation_number: form.generation_number,
      courtesy_name: form.courtesy_name || null,
      birth_date: form.birth_date || null,
      death_date: form.death_date || null,
      birth_place: form.birth_place || null,
      father_id: form.father_id,
      mother_id: form.mother_id,
      spouse_name: form.spouse_name || null,
      photo: form.photo || null,
      notes: form.notes || null,
    }
    if (isEdit) {
      await api.put(`/members/${id}`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/members', { ...payload, genealogy_id: gid })
      ElMessage.success('创建成功')
    }
    goBack()
  } catch (e) {
    ElMessage.error('保存失败')
    console.error(e)
  } finally {
    submitting.value = false
  }
}

function goBack() {
  if (form.genealogy_id) {
    router.push(`/genealogy/${form.genealogy_id}/members`)
  } else {
    router.push('/member')
  }
}

watch(() => route.params.id, fetchData, { immediate: true })
watch(() => route.query.genealogyId, () => {
  const q = route.query.genealogyId as string | undefined
  if (q && !form.genealogy_id) form.genealogy_id = parseInt(q, 10)
})
onMounted(() => {
  fetchGenealogies()
  fetchData()
})
</script>

<style scoped>
.member-form { padding: 20px; max-width: 600px; }
.mt-2 { margin-top: 8px; }
</style>
