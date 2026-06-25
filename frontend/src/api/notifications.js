import { api } from './client'

export const notificationsApi = {
  getQQGroup() {
    return api.get('/notifications/qq-group')
  },
  updateQQGroup(payload) {
    return api.put('/notifications/qq-group', payload)
  },
  regenerateQQGroupCode() {
    return api.post('/notifications/qq-group/regenerate-code')
  },
  manualBindQQGroup(payload) {
    return api.post('/notifications/qq-group/manual-bind', payload)
  },
  testQQGroup() {
    return api.post('/notifications/qq-group/test')
  }
}
