import { computed, ref } from 'vue'

export const THEME_STORAGE_KEY = 'registro_theme'
const VALID_THEMES = new Set(['dark', 'light'])
const theme = ref(readStoredTheme())
const isThemeTransitioning = ref(false)
let activeThemeTransition = null

function readStoredTheme() {
  if (typeof window === 'undefined') return 'dark'
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
  return VALID_THEMES.has(stored) ? stored : 'dark'
}

export function applyTheme(themeName = theme.value) {
  const nextTheme = VALID_THEMES.has(themeName) ? themeName : 'dark'
  theme.value = nextTheme
  if (typeof document !== 'undefined') {
    document.documentElement.dataset.theme = nextTheme
    document.documentElement.style.colorScheme = nextTheme
  }
}

export function initializeTheme() {
  applyTheme(readStoredTheme())
}

function prefersReducedMotion() {
  return typeof window !== 'undefined'
    && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true
}

function applyThemeWithTransition(nextTheme) {
  if (typeof document === 'undefined' || prefersReducedMotion() || typeof document.startViewTransition !== 'function') {
    applyTheme(nextTheme)
    return Promise.resolve()
  }

  isThemeTransitioning.value = true

  try {
    const transition = document.startViewTransition(() => {
      applyTheme(nextTheme)
    })

    const finished = Promise.resolve(transition?.finished)
    activeThemeTransition = finished
      .catch(() => {})
      .finally(() => {
        isThemeTransitioning.value = false
        activeThemeTransition = null
      })

    return activeThemeTransition
  } catch {
    applyTheme(nextTheme)
    isThemeTransitioning.value = false
    activeThemeTransition = null
    return Promise.resolve()
  }
}

export function useTheme() {
  const isDark = computed(() => theme.value === 'dark')

  function setTheme(nextTheme, { animate = true } = {}) {
    const normalized = VALID_THEMES.has(nextTheme) ? nextTheme : 'dark'

    if (isThemeTransitioning.value) return activeThemeTransition || Promise.resolve()

    if (typeof window !== 'undefined') {
      window.localStorage.setItem(THEME_STORAGE_KEY, normalized)
    }

    if (normalized === theme.value) return Promise.resolve()

    return animate
      ? applyThemeWithTransition(normalized)
      : (applyTheme(normalized), Promise.resolve())
  }

  function toggleTheme(options = {}) {
    return setTheme(isDark.value ? 'light' : 'dark', options)
  }

  return {
    theme,
    isDark,
    isThemeTransitioning: computed(() => isThemeTransitioning.value),
    setTheme,
    toggleTheme,
  }
}
