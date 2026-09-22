import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import MobileBottomNavigation from './MobileBottomNavigation.vue'

const items = [
  {
    key: 'home',
    label: 'Inicio',
    accessibleLabel: 'Inicio',
    mobileLabel: 'Inicio',
    icon: 'home',
    to: { name: 'home' },
  },
]

function mountNavigation(props = {}) {
  return mount(MobileBottomNavigation, {
    props: { items, ...props },
    global: {
      stubs: {
        RouterLink: {
          props: ['to'],
          template: '<a v-bind="$attrs" :href="to.name"><slot /></a>',
        },
        NavigationIcon: true,
        AppIcon: true,
      },
    },
  })
}

describe('MobileBottomNavigation', () => {
  it('marks the current route and exposes the full accessible link name', () => {
    const wrapper = mountNavigation({ activeKey: 'home' })
    const homeLink = wrapper.get('a[href="home"]')

    expect(homeLink.attributes('aria-current')).toBe('page')
    expect(homeLink.attributes('aria-label')).toBe('Inicio')
  })

  it('opens the More options panel without targeting the sidebar', async () => {
    const wrapper = mountNavigation({ moreExpanded: false })
    const moreButton = wrapper.get('button[aria-controls="app-mobile-more-panel"]')

    expect(moreButton.attributes('aria-expanded')).toBe('false')
    await moreButton.trigger('click')

    expect(wrapper.emitted('open-more')).toHaveLength(1)
    expect(wrapper.emitted('open-more')[0][0]).toBeTruthy()
    expect(moreButton.attributes('aria-expanded')).toBe('false')
    await wrapper.setProps({ moreExpanded: true })
    expect(moreButton.attributes('aria-expanded')).toBe('true')
    expect(moreButton.attributes('aria-label')).toBe('Cerrar más opciones')
  })

  it('keeps More in a dedicated fifth slot after scrolling', async () => {
    const directItems = Array.from({ length: 4 }, (_, index) => ({
      ...items[0],
      key: `destination-${index + 1}`,
      mobileLabel: `Destino ${index + 1}`,
    }))
    const wrapper = mountNavigation({ items: directItems })
    const surface = wrapper.get('.app-mobile-bottom-navigation__surface')

    expect(surface.classes()).toContain('grid-cols-5')
    expect(surface.element.children).toHaveLength(5)
    expect(wrapper.get('button[aria-controls="app-mobile-more-panel"]').text()).toContain('Más')

    window.dispatchEvent(new Event('scroll'))
    await wrapper.vm.$nextTick()

    expect(wrapper.get('button[aria-controls="app-mobile-more-panel"]').exists()).toBe(true)
  })

  it('shows a pending badge without replacing the link name', () => {
    const wrapper = mountNavigation({
      items: [{
        ...items[0],
        key: 'pendientes',
        label: 'Pendientes',
        accessibleLabel: 'Pendientes',
        mobileLabel: 'Pendientes',
        badge: 3,
      }],
    })

    expect(wrapper.get('a').attributes('aria-label')).toBe('Pendientes, 3 pendientes')
    expect(wrapper.text()).toContain('3')
  })
})
