import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ref } from 'vue'

const routerPush = vi.hoisted(() => vi.fn())

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: routerPush }),
}))

import { CHROME_PLAY_STORE_URL } from '@/composables/usePwaInstallStatus'
import ConfiguracionView from './ConfiguracionView.vue'

const originalMatchMediaDescriptor = Object.getOwnPropertyDescriptor(window, 'matchMedia')
const originalUserAgentDescriptor = Object.getOwnPropertyDescriptor(
  window.navigator,
  'userAgent',
)

function setBrowser({ standalone = false, userAgent = 'Mozilla/5.0 Chrome/126.0' } = {}) {
  Object.defineProperty(window, 'matchMedia', {
    configurable: true,
    writable: true,
    value: vi.fn(() => ({
      matches: standalone,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  })
  Object.defineProperty(window.navigator, 'userAgent', {
    configurable: true,
    get: () => userAgent,
  })
}

function mountView({ installPrompt = null, installApp = vi.fn() } = {}) {
  return mount(ConfiguracionView, {
    global: {
      provide: {
        pwaInstall: {
          deferredInstallPrompt: ref(installPrompt),
          installApp,
        },
      },
      stubs: {
        AppIcon: true,
        PageHeader: true,
      },
    },
  })
}

describe('ConfiguracionView PWA installation', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    routerPush.mockReset()
    setBrowser()
  })

  afterEach(() => {
    if (originalMatchMediaDescriptor) {
      Object.defineProperty(window, 'matchMedia', originalMatchMediaDescriptor)
    } else {
      delete window.matchMedia
    }
    if (originalUserAgentDescriptor) {
      Object.defineProperty(window.navigator, 'userAgent', originalUserAgentDescriptor)
    } else {
      delete window.navigator.userAgent
    }
  })

  it('shows the native install action when beforeinstallprompt is available', async () => {
    const installApp = vi.fn()
    const beforeInstallPrompt = {
      prompt: vi.fn(),
      userChoice: Promise.resolve({ outcome: 'accepted' }),
    }
    const wrapper = mountView({ installPrompt: beforeInstallPrompt, installApp })

    expect(wrapper.find('[data-testid="pwa-install-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pwa-manual-install"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="chrome-play-link"]').attributes('href')).toBe(
      CHROME_PLAY_STORE_URL,
    )

    await wrapper.find('[data-testid="pwa-install-button"]').trigger('click')
    expect(installApp).toHaveBeenCalledOnce()
  })

  it('shows the installed state when running in standalone mode', () => {
    setBrowser({ standalone: true })
    const wrapper = mountView()

    expect(wrapper.find('[data-testid="pwa-installed-message"]').text()).toContain(
      'Ya tenés la app instalada en tu pantalla de inicio.',
    )
    expect(wrapper.find('[data-testid="pwa-install-button"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="pwa-manual-install"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="chrome-play-link"]').exists()).toBe(false)
  })

  it('shows Mi Browser instructions and the Chrome workaround without a native prompt', () => {
    setBrowser({
      userAgent:
        'Mozilla/5.0 (Linux; U; Android 15) AppleWebKit/537.36 MiuiBrowser/18.5.120514 Mobile Safari/537.36',
    })
    const wrapper = mountView()
    const manualFallback = wrapper.find('[data-testid="pwa-manual-install"]')
    const chromeLink = wrapper.find('[data-testid="chrome-play-link"]')

    expect(manualFallback.text()).toContain(
      'Mi Browser no ofrece el botón automático de instalación.',
    )
    expect(manualFallback.text()).toContain('Agregar a la pantalla de inicio')
    expect(chromeLink.attributes('href')).toBe(CHROME_PLAY_STORE_URL)
    expect(chromeLink.attributes('target')).toBe('_blank')
    expect(chromeLink.attributes('rel')).toBe('noopener noreferrer')
  })
})
