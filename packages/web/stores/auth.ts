export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: '' as string,
    username: '' as string,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    init() {
      if (import.meta.client) {
        this.token = localStorage.getItem('auth_token') || ''
        this.username = localStorage.getItem('auth_username') || ''
      }
    },
    setAuth(token: string, username: string) {
      this.token = token
      this.username = username
      if (import.meta.client) {
        localStorage.setItem('auth_token', token)
        localStorage.setItem('auth_username', username)
      }
    },
    logout() {
      this.token = ''
      this.username = ''
      if (import.meta.client) {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_username')
      }
    },
  },
})
