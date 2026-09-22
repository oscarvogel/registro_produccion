import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ThemeToggle from './ThemeToggle.vue'
import { applyTheme } from '@/composables/useTheme'

const originalMatchMedia = Object.getOwnPropertyDescriptor(window, 'matchMedia')

function mountToggle(variant = 'sidebar') {
  return mount(ThemeToggle, {
    props: { variant },
    global: {
      stubs: {
        AppIcon: { template: '<span aria-hidden="true"></span>' },
      },
    },
  })
}

describe('ThemeToggle', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      value: () => ({ matches: false }),
    })
    delete document.startViewTransition
    applyTheme('dark')
  })

  afterEach(() => {
    if (originalMatchMedia) Object.defineProperty(window, 'matchMedia', originalMatchMedia)
    else delete window.matchMedia
  })

  it('exposes an accessible sidebar toggle and changes its label', async () => {
    const wrapper = mountToggle()
    const button = wrapper.get('[data-testid="theme-toggle"]')

    expect(button.attributes('aria-label')).toBe('Cambiar a modo claro')
    await button.trigger('click')

    expect(button.attributes('aria-label')).toBe('Cambiar a modo oscuro')
    expect(button.text()).toContain('Modo claro')
  })

  it('keeps the settings variant available with the same behavior', async () => {
    const wrapper = mountToggle('settings')
    const button = wrapper.get('[data-testid="theme-toggle"]')

    expect(button.text()).toContain('Modo oscuro activo')
    await button.trigger('click')
    expect(button.text()).toContain('Modo claro activo')
  })
})
