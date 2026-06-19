import { defineStore } from 'pinia'

let nextId = 1
const DEFAULT_DEDUPE_MS = 3500

export const useToastStore = defineStore('toast', {
  state: () => ({
    items: [],
    recentKeys: {},
  }),

  actions: {
    push({ title, message = '', tone = 'neutral', timeout = 4500, dedupeMs = DEFAULT_DEDUPE_MS }) {
      const key = `${tone}|${title}|${message}`
      const now = Date.now()
      const lastShownAt = this.recentKeys[key] || 0
      if (dedupeMs > 0 && Object.prototype.hasOwnProperty.call(this.recentKeys, key) && now - lastShownAt < dedupeMs) {
        return null
      }
      this.recentKeys[key] = now
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
