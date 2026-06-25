import { defineStore } from 'pinia'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
    initialized: false
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.user && localStorage.getItem('access_token'))
  },
  actions: {
    setTokens(tokens) {
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
    },
    async fetchMe() {
      const { data } = await authApi.me()
      this.user = data
      this.initialized = true
      return data
    },
    async init() {
      if (!localStorage.getItem('access_token')) {
        this.initialized = true
        return
      }
      try {
        await this.fetchMe()
      } catch {
        this.logout()
      } finally {
        this.initialized = true
      }
    },
    async login(payload) {
      this.loading = true
      try {
        const { data } = await authApi.login(payload)
        this.setTokens(data)
        await this.fetchMe()
      } finally {
        this.loading = false
      }
    },
    async register(payload) {
      this.loading = true
      try {
        const { data } = await authApi.register(payload)
        this.setTokens(data)
        await this.fetchMe()
      } finally {
        this.loading = false
      }
    },
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      this.user = null
      this.initialized = true
    }
  }
})
