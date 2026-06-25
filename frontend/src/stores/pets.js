import { defineStore } from 'pinia'
import { petsApi } from '../api/pets'

export const usePetsStore = defineStore('pets', {
  state: () => ({
    pets: [],
    loading: false
  }),
  getters: {
    currentPet: (state) => (id) => state.pets.find((pet) => pet.id === id) || state.pets[0] || null
  },
  actions: {
    async fetchPets() {
      this.loading = true
      try {
        const { data } = await petsApi.list()
        this.pets = data
      } finally {
        this.loading = false
      }
    },
    async createPet(payload) {
      const { data } = await petsApi.create(payload)
      this.pets.unshift(data)
      return data
    },
    async updatePet(id, payload) {
      const { data } = await petsApi.update(id, payload)
      const index = this.pets.findIndex((pet) => pet.id === id)
      if (index >= 0) {
        this.pets[index] = data
      }
      return data
    },
    async removePet(id) {
      await petsApi.remove(id)
      this.pets = this.pets.filter((pet) => pet.id !== id)
    }
  }
})
