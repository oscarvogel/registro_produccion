import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  THEME_STORAGE_KEY,
  applyTheme,
  useTheme,
} from './useTheme'

const originalMatchMedia = Object.getOwnPropertyDescriptor(window, 'matchMedia')
const originalStartViewTransition = Object.getOwnPropertyDescriptor(document, 'startViewTransition')

function setReducedMotion(matches = false) {
  Object.defineProperty(window, 'matchMedia', {
    configurable: true,
    value: vi.fn(() => ({ matches })),
  })
}

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    setReducedMotion(false)
    delete document.startViewTransition
    applyTheme('dark')
  })

  afterEach(() => {
    if (originalMatchMedia) Object.defineProperty(window, 'matchMedia', originalMatchMedia)
    else delete window.matchMedia

    if (originalStartViewTransition) Object.defineProperty(document, 'startViewTransition', originalStartViewTransition)
    else delete document.startViewTransition
  })

  it('changes and persists the theme without requiring View Transition API', async () => {
    const { isDark, setTheme } = useTheme()

    await setTheme('light')

    expect(isDark.value).toBe(false)
    expect(document.documentElement.dataset.theme).toBe('light')
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('light')
  })

  it('uses the browser transition when available', async () => {
    const finished = Promise.resolve()
    const startViewTransition = vi.fn((callback) => {
      callback()
      return { finished }
    })
    Object.defineProperty(document, 'startViewTransition', {
      configurable: true,
      value: startViewTransition,
    })

    const { toggleTheme, isThemeTransitioning } = useTheme()
    const transition = toggleTheme()

    expect(startViewTransition).toHaveBeenCalledOnce()
    expect(isThemeTransitioning.value).toBe(true)
    await transition
    expect(isThemeTransitioning.value).toBe(false)
    expect(document.documentElement.dataset.theme).toBe('light')
  })

  it('skips the advanced transition when reduced motion is requested', async () => {
    setReducedMotion(true)
    const startViewTransition = vi.fn()
    Object.defineProperty(document, 'startViewTransition', {
      configurable: true,
      value: startViewTransition,
    })

    await useTheme().toggleTheme()

    expect(startViewTransition).not.toHaveBeenCalled()
    expect(document.documentElement.dataset.theme).toBe('light')
  })

  it('ignores a second toggle while a transition is active', async () => {
    let resolveFinished
    const finished = new Promise((resolve) => {
      resolveFinished = resolve
    })
    const startViewTransition = vi.fn((callback) => {
      callback()
      return { finished }
    })
    Object.defineProperty(document, 'startViewTransition', {
      configurable: true,
      value: startViewTransition,
    })

    const { toggleTheme } = useTheme()
    const first = toggleTheme()
    const second = toggleTheme()

    expect(startViewTransition).toHaveBeenCalledOnce()
    expect(second).toBe(first)

    resolveFinished()
    await first
  })
})
