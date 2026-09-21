import { afterEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import MobileMoreMenu from './MobileMoreMenu.vue'

const mountedWrappers = []

function mountMenu(props = {}) {
  const wrapper = mount(MobileMoreMenu, {
    props: {
      open: true,
      groups: [{
        key: 'produccion',
        label: 'Producción',
        items: [{
          key: 'pendientes',
          label: 'Pendientes',
          accessibleLabel: 'Pendientes',
          icon: 'pending',
          to: { name: 'pendientes' },
          badge: 3,
        }],
      }],
      ...props,
    },
    global: {
      stubs: {
        RouterLink: {
          props: ['to'],
          emits: ['click'],
          template: '<a v-bind="$attrs" :href="to.name" @click.prevent="$emit(\'click\', $event)"><slot /></a>',
        },
        NavigationIcon: true,
        AppIcon: true,
      },
    },
  })
  mountedWrappers.push(wrapper)
  return wrapper
}

afterEach(() => {
  mountedWrappers.splice(0).forEach((wrapper) => wrapper.unmount())
})

describe('MobileMoreMenu', () => {
  it('renders secondary destinations with active state and pending count', () => {
    const wrapper = mountMenu({ activeKey: 'pendientes' })
    const pendingLink = wrapper.get('a[href="pendientes"]')

    expect(wrapper.get('#app-mobile-more-panel').attributes('aria-label')).toBe('Más opciones')
    expect(pendingLink.attributes('aria-current')).toBe('page')
    expect(pendingLink.attributes('aria-label')).toBe('Pendientes, 3 pendientes')
  })

  it('closes the panel after selecting a destination', async () => {
    const wrapper = mountMenu()

    await wrapper.get('a[href="pendientes"]').trigger('click')

    expect(wrapper.emitted('navigate')).toHaveLength(1)
  })

  it('closes on Escape and restores focus to the More trigger', () => {
    const trigger = document.createElement('button')
    document.body.append(trigger)
    const wrapper = mountMenu({ triggerElement: trigger })

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }))

    expect(wrapper.emitted('close')).toHaveLength(1)
    expect(document.activeElement).toBe(trigger)
    trigger.remove()
  })

  it('closes when the user clicks outside the panel and trigger', () => {
    const wrapper = mountMenu()

    document.body.dispatchEvent(new MouseEvent('click', { bubbles: true }))

    expect(wrapper.emitted('close')).toHaveLength(1)
  })
})
