import { api } from './client'

export const growthApi = {
  list(petId) {
    return api.get(`/pets/${petId}/growth`)
  },
  create(petId, payload) {
    return api.post(`/pets/${petId}/growth`, payload)
  }
}
