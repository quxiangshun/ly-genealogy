<template>
  <div class="wiki-form">
    <el-form :model="form" label-width="120px" v-loading="loading">
      <el-form-item label="标题" required>
        <el-input v-model="form.title" placeholder="标题" @blur="autoSlug" />
      </el-form-item>
      <el-form-item label="Slug">
        <el-input v-model="form.slug" placeholder="URL标识，留空自动生成" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="form.category" placeholder="分类" style="width: 200px">
          <el-option label="起源" value="origin" />
          <el-option label="名人" value="celebrity" />
          <el-option label="堂号" value="hall" />
          <el-option label="习俗" value="custom" />
          <el-option label="文物" value="relic" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      <el-form-item label="年代">
        <el-input v-model="form.era" placeholder="如：战国" />
      </el-form-item>
      <el-form-item label="摘要">
        <el-input v-model="form.summary" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="正文">
        <MdEditor v-model="form.content" language="zh-CN" />
      </el-form-item>
      <el-form-item label="封面图">
        <el-input v-model="form.cover_image" placeholder="封面图URL" />
      </el-form-item>
      <el-form-item label="排序">
        <el-input-number v-model="form.sort_order" :min="0" />
      </el-form-item>
      <el-form-item label="已发布">
        <el-switch v-model="form.is_published" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submit" :loading="submitting">保存</el-button>
        <el-button @click="router.push('/wiki')">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { api } from '../../api/index'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string | undefined
const isEdit = !!id

function slugify(s: string): string {
  return s
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\u4e00-\u9fa5a-zA-Z0-9-]/g, '')
    .toLowerCase()
}

const form = reactive({
  title: '',
  slug: '',
  category: 'other',
  era: '',
  summary: '',
  content: '',
  cover_image: '',
  sort_order: 0,
  is_published: true,
})

const loading = ref(false)
const submitting = ref(false)

function autoSlug() {
  if (!isEdit && form.title && !form.slug) {
    form.slug = slugify(form.title)
  }
}

async function fetchData() {
  if (!id) return
  loading.value = true
  try {
    const res = await api.get<Record<string, unknown>>(`/wiki/id/${id}`)
    const d = res.data
    if (d) {
      form.title = String(d.title ?? '')
      form.slug = String(d.slug ?? '')
      form.category = String(d.category ?? 'other')
      form.era = String(d.era ?? '')
      form.summary = String(d.summary ?? '')
      form.content = String(d.content ?? '')
      form.cover_image = String(d.cover_image ?? '')
      form.sort_order = Number(d.sort_order ?? 0)
      form.is_published = !!(d.is_published ?? 1)
    }
  } catch (e) {
    ElMessage.error('加载失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!form.title) {
    ElMessage.warning('请填写标题')
    return
  }
  submitting.value = true
  try {
    const payload = {
      title: form.title,
      slug: form.slug || undefined,
      category: form.category,
      era: form.era || null,
      summary: form.summary || null,
      content: form.content || '',
      cover_image: form.cover_image || null,
      sort_order: form.sort_order,
      is_published: form.is_published,
    }
    if (isEdit) {
      await api.put(`/wiki/${id}`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/wiki', payload)
      ElMessage.success('创建成功')
    }
    router.push('/wiki')
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
.wiki-form { padding: 20px; max-width: 900px; }
</style>
