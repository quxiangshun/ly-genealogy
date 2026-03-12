<template>
  <div class="change-pwd-wrapper">
    <el-card class="change-pwd-card">
      <template #header>
        <div class="card-header">
          <span class="logo-text">修改密码</span>
          <p class="hint" v-if="auth.mustChangePassword">首次登录必须修改默认密码后才能操作</p>
          <p class="hint" v-else>修改您的登录密码</p>
        </div>
      </template>
      <el-alert
        v-if="auth.mustChangePassword"
        title="安全提示：您正在使用默认密码，为保障账户安全，请立即修改密码。"
        type="warning"
        :closable="false"
        show-icon
        class="pwd-alert"
      />
      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit">
        <el-form-item prop="oldPassword" label="原密码">
          <el-input v-model="form.oldPassword" type="password" show-password size="large" />
        </el-form-item>
        <el-form-item prop="newPassword" label="新密码">
          <el-input v-model="form.newPassword" type="password" show-password size="large" />
        </el-form-item>
        <el-form-item prop="confirmPassword" label="确认密码">
          <el-input v-model="form.confirmPassword" type="password" show-password size="large" @keyup.enter="handleSubmit" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" class="submit-btn" @click="handleSubmit">
            确认修改
          </el-button>
          <el-button v-if="!auth.mustChangePassword" size="large" class="submit-btn" @click="router.push('/dashboard')">
            取消
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
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

const rules: FormRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_: unknown, value: string, callback: (err?: Error) => void) => {
        if (value !== form.newPassword) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await auth.changePassword(form.oldPassword, form.newPassword)
      ElMessage.success('密码修改成功，欢迎使用系统')
      const redirect = (route.query.redirect as string) || '/dashboard'
      router.push(redirect)
    } catch (err: unknown) {
      const axErr = err as { response?: { data?: { error?: string } } }
      ElMessage.error(axErr?.response?.data?.error || '修改失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.change-pwd-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40px 20px;
}
.change-pwd-card { width: 420px; }
.card-header { text-align: center; }
.logo-text { font-size: 20px; font-weight: 600; color: #c9a227; }
.hint { font-size: 13px; color: #999; margin: 6px 0 0; }
.pwd-alert { margin-bottom: 20px; }
.submit-btn { width: 100%; margin-left: 0 !important; margin-top: 4px; }
</style>
