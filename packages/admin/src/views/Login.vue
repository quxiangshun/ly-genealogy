<template>
  <div class="login-page">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span class="logo-text">屈氏宗谱管理</span>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const data = await auth.login(form.username, form.password)
      if (data.mustChangePassword) {
        router.push({ path: '/change-password', query: route.query })
      } else {
        const redirect = (route.query.redirect as string) || '/dashboard'
        router.push(redirect)
      }
    } catch (err: unknown) {
      const axErr = err as { response?: { data?: { error?: string; message?: string } } }
      ElMessage.error(axErr?.response?.data?.error || axErr?.response?.data?.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(ellipse at 30% 20%, rgba(156,118,56,0.12) 0%, transparent 55%),
    radial-gradient(ellipse at 70% 80%, rgba(122,46,34,0.08) 0%, transparent 45%),
    linear-gradient(135deg, #231808 0%, #2c1e0e 40%, #1c1708 100%);
}

.login-card {
  width: 400px;
  --el-card-bg-color: var(--admin-paper);
  border-color: var(--admin-border);
  box-shadow: 0 8px 40px rgba(28,23,8,0.4);
}

.card-header {
  text-align: center;
}

.logo-text {
  font-family: var(--font-title);
  font-size: 24px;
  font-weight: 700;
  color: var(--admin-gold-bright);
  letter-spacing: 0.15em;
}

.login-btn {
  width: 100%;
  --el-button-bg-color: var(--admin-accent);
  --el-button-border-color: var(--admin-accent);
}
</style>
