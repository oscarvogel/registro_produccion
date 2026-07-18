import { defineStore } from 'pinia'
import api, { getUserSafeErrorMessage } from '@/services/api'

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchItems() {
      this.loading = true
      try {
        const { data } = await api.get('/api/items')
        this.items = data
      } catch (err) {
        this.error = getUserSafeErrorMessage(err, 'No se pudieron cargar los items')
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
