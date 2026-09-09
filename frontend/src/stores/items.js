import { defineStore } from 'pinia'
import api from '@/services/api'

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchItems() {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get('/api/items', { _suppressErrorToast: true })
        this.items = data
      } catch (err) {
        this.error = err.response?.data?.detail || 'No se pudieron cargar los items.'
        this.items = []
      } finally {
        this.loading = false
      }
    },
    
    async createItem(item) {
      const { data } = await api.post('/api/items', item)
      this.items.push(data)
      return data
    }
  }
})
