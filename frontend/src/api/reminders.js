import { api } from './client'

export const remindersApi = {
  list() {
    return api.get('/reminders')
  },
  today() {
    return api.get('/reminders/today')
  },
  create(payload) {
    return api.post('/reminders', payload)
  },
  complete(id) {
    return api.put(`/reminders/${id}/complete`)
  }
}
