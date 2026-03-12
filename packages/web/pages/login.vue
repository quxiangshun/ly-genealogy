<template>
  <div class="row justify-content-center">
    <div class="col-md-5">
      <div class="card heritage-card">
        <div class="card-header">
          <i class="bi bi-person-circle me-2" />登录
        </div>
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label class="form-label" for="username">用户名</label>
              <input
                id="username"
                v-model="form.username"
                type="text"
                class="form-control"
                required
                autocomplete="username"
              >
            </div>
            <div class="mb-3">
              <label class="form-label" for="password">密码</label>
              <input
                id="password"
                v-model="form.password"
                type="password"
                class="form-control"
                required
                autocomplete="current-password"
              >
            </div>
            <div v-if="error" class="alert alert-danger heritage-alert py-2">
              {{ error }}
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-1" />
              登录
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
  username: '',
  password: '',
})
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    const res = await api<{
      token: string
      username: string
      mustChangePassword?: boolean
    }>('/auth/login', {
      method: 'POST',
      body: form,
    })
    authStore.setAuth(res.token, res.username)
    if (res.mustChangePassword) {
      await navigateTo('/change-password')
    } else {
      await navigateTo('/')
    }
  } catch (e: unknown) {
    const err = e as { data?: { error?: string }; statusMessage?: string }
    error.value = err?.data?.error ?? err?.statusMessage ?? '登录失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  authStore.init()
})

useHead({
  title: '登录 - 屈氏宗谱',
})
</script>
