import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useToastStore } from './toast'


describe('toast store', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    setActivePinia(createPinia())
  })

  it('removes a toast after its timeout', () => {
    const store = useToastStore()

    store.push({ title: 'Listo', timeout: 1000 })

    expect(store.items).toHaveLength(1)

    vi.advanceTimersByTime(1000)

    expect(store.items).toHaveLength(0)
  })
})
