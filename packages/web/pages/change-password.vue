<template>
  <div class="row justify-content-center">
    <div class="col-md-5">
      <div class="card heritage-card">
        <div class="card-header">
          <i class="bi bi-key me-2" />修改密码
        </div>
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label class="form-label" for="oldPassword">原密码</label>
              <input
                id="oldPassword"
                v-model="form.oldPassword"
                type="password"
                class="form-control"
                required
                autocomplete="current-password"
              >
            </div>
            <div class="mb-3">
              <label class="form-label" for="newPassword">新密码</label>
              <input
                id="newPassword"
                v-model="form.newPassword"
                type="password"
                class="form-control"
                required
                autocomplete="new-password"
              >
            </div>
            <div class="mb-3">
              <label class="form-label" for="confirmPassword">确认新密码</label>
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                type="password"
                class="form-control"
                required
                autocomplete="new-password"
              >
            </div>
            <div v-if="error" class="alert alert-danger heritage-alert py-2">
              {{ error }}
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-1" />
              修改密码
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const { api } = useApi()
const authStore = useAuthStore()

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  if (form.newPassword !== form.confirmPassword) {
    error.value = '两次输入的新密码不一致'
    return
  }
  loading.value = true
  try {
    await api('/auth/change-password', {
      method: 'POST',
      body: {
        oldPassword: form.oldPassword,
        newPassword: form.newPassword,
      },
    })
    await navigateTo('/')
  } catch (e: unknown) {
    const err = e as { data?: { error?: string }; statusMessage?: string }
    error.value = err?.data?.error ?? err?.statusMessage ?? '修改失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  authStore.init()
  if (!authStore.isLoggedIn) {
    navigateTo('/login')
  }
})

useHead({
  title: '修改密码 - 屈氏宗谱',
})
</script>
