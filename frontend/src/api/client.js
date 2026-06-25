import axios from 'axios'

export const api = axios.create({
  baseURL: '/api'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status !== 401) {
      throw error
    }

    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken || error.config.__retried) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      throw error
    }

    error.config.__retried = true
    const { data } = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    error.config.headers.Authorization = `Bearer ${data.access_token}`
    return api(error.config)
  }
)
