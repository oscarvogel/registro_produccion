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

  it('deduplicates repeated equal toasts inside the configured window', () => {
    const store = useToastStore()

    store.error('Error del servidor', 'No se pudo conectar con el servidor.')
    store.error('Error del servidor', 'No se pudo conectar con el servidor.')

    expect(store.items).toHaveLength(1)

    vi.advanceTimersByTime(4000)
    store.error('Error del servidor', 'No se pudo conectar con el servidor.')

    expect(store.items).toHaveLength(2)
  })
})
