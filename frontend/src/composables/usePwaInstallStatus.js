import { computed, onMounted, onUnmounted, ref, unref } from 'vue'

export const PWA_DISPLAY_MODE_QUERY = '(display-mode: standalone)'
export const CHROME_PLAY_STORE_URL =
  'https://play.google.com/store/apps/details?id=com.android.chrome'

export function isXiaomiBrowserUserAgent(userAgent = '') {
  return /MiuiBrowser|Mi Browser|Mint Browser/i.test(userAgent)
}

export function isStandaloneDisplay(windowObject, navigatorObject) {
  const matchesStandalone =
    typeof windowObject?.matchMedia === 'function' &&
    windowObject.matchMedia(PWA_DISPLAY_MODE_QUERY).matches

  return Boolean(matchesStandalone || navigatorObject?.standalone === true)
}

export function usePwaInstallStatus(
  pwaInstall,
  {
    windowObject = typeof window !== 'undefined' ? window : undefined,
    navigatorObject = typeof navigator !== 'undefined' ? navigator : undefined,
  } = {},
) {
  const displayModeQuery =
    typeof windowObject?.matchMedia === 'function'
      ? windowObject.matchMedia(PWA_DISPLAY_MODE_QUERY)
      : null

  const isStandalone = ref(isStandaloneDisplay(windowObject, navigatorObject))
  const isXiaomiBrowser = ref(
    isXiaomiBrowserUserAgent(navigatorObject?.userAgent || ''),
  )
  const canInstall = computed(
    () => !isStandalone.value && Boolean(unref(pwaInstall?.deferredInstallPrompt)),
  )

  function updateDisplayMode() {
    isStandalone.value = isStandaloneDisplay(windowObject, navigatorObject)
  }

  onMounted(() => {
    if (typeof displayModeQuery?.addEventListener === 'function') {
      displayModeQuery.addEventListener('change', updateDisplayMode)
    } else if (typeof displayModeQuery?.addListener === 'function') {
      displayModeQuery.addListener(updateDisplayMode)
    }
  })

  onUnmounted(() => {
    if (typeof displayModeQuery?.removeEventListener === 'function') {
      displayModeQuery.removeEventListener('change', updateDisplayMode)
    } else if (typeof displayModeQuery?.removeListener === 'function') {
      displayModeQuery.removeListener(updateDisplayMode)
    }
  })

  return {
    canInstall,
    isStandalone,
    isXiaomiBrowser,
  }
}
