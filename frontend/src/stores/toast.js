import { defineStore } from 'pinia'

let nextId = 1

export const useToastStore = defineStore('toast', {
  state: () => ({
    items: [],
  }),

  actions: {
    push({ title, message = '', tone = 'neutral', timeout = 4500 }) {
      const id = nextId++
      this.items.push({ id, title, message, tone })
      if (timeout > 0) {
        window.setTimeout(() => this.remove(id), timeout)
      }
      return id
    },

    success(title, message = '') {
      return this.push({ title, message, tone: 'success' })
    },

    error(title, message = '') {
      return this.push({ title, message, tone: 'error', timeout: 6500 })
    },

    info(title, message = '') {
      return this.push({ title, message, tone: 'info' })
    },

    remove(id) {
      this.items = this.items.filter((item) => item.id !== id)
    },
  },
})
