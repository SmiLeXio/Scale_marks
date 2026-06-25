import { api } from './client'

export const petsApi = {
  list() {
    return api.get('/pets')
  },
  create(payload) {
    return api.post('/pets', payload)
  },
  update(id, payload) {
    return api.put(`/pets/${id}`, payload)
  },
  remove(id) {
    return api.delete(`/pets/${id}`)
  }
}
