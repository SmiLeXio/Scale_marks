import { api } from './client'

export const feedingApi = {
  list(petId) {
    return api.get(`/pets/${petId}/feeding`)
  },
  create(petId, payload) {
    return api.post(`/pets/${petId}/feeding`, payload)
  },
  calculate(petId) {
    return api.get(`/pets/${petId}/feeding/calculate`)
  }
}
