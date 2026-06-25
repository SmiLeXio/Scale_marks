import { api } from './client'

export const authApi = {
  register(payload) {
    return api.post('/auth/register', payload)
  },
  login(payload) {
    return api.post('/auth/login', payload)
  },
  me() {
    return api.get('/auth/me')
  }
}
