import { defineStore } from 'pinia'
import { api } from '../api/index'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('admin_token') || '',
    username: localStorage.getItem('admin_username') || '',
    mustChangePassword: localStorage.getItem('admin_must_change_pwd') === '1',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    async login(username: string, password: string) {
      const res = await api.post('/auth/login', { username, password })
      this.token = res.data.token
      this.username = username
      this.mustChangePassword = !!res.data.mustChangePassword
      localStorage.setItem('admin_token', this.token)
      localStorage.setItem('admin_username', username)
      localStorage.setItem('admin_must_change_pwd', this.mustChangePassword ? '1' : '0')
      return res.data
    },
    logout() {
      this.token = ''
      this.username = ''
      this.mustChangePassword = false
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_username')
      localStorage.removeItem('admin_must_change_pwd')
    },
    async changePassword(oldPassword: string, newPassword: string) {
      await api.post('/auth/change-password', { oldPassword, newPassword })
      this.mustChangePassword = false
      localStorage.setItem('admin_must_change_pwd', '0')
    },
  },
})
