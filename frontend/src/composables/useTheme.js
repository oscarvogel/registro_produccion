import { computed, ref } from 'vue'

export const THEME_STORAGE_KEY = 'registro_theme'
const VALID_THEMES = new Set(['dark', 'light'])
const theme = ref(readStoredTheme())

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

export function useTheme() {
  const isDark = computed(() => theme.value === 'dark')

  function setTheme(nextTheme) {
    const normalized = VALID_THEMES.has(nextTheme) ? nextTheme : 'dark'
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(THEME_STORAGE_KEY, normalized)
    }
    applyTheme(normalized)
  }

  function toggleTheme() {
    setTheme(isDark.value ? 'light' : 'dark')
  }

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
  }
}
