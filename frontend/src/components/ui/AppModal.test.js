import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { afterEach, describe, expect, it } from 'vitest'

import AppModal from './AppModal.vue'

describe('AppModal', () => {
  const mountedWrappers = []

  afterEach(() => {
    mountedWrappers.forEach((wrapper) => wrapper.unmount())
    mountedWrappers.length = 0
    document.body.innerHTML = ''
  })

  async function mountOpenModal(slot = {}) {
    const trigger = document.createElement('button')
    trigger.type = 'button'
    trigger.textContent = 'Abrir modal'
    document.body.appendChild(trigger)
    trigger.focus()

    const wrapper = mount(AppModal, {
      attachTo: document.body,
      props: {
        modelValue: true,
        title: 'Título de prueba',
      },
      slots: slot,
      global: {
        directives: {
          'motion-pop': {},
        },
      },
    })
    mountedWrappers.push(wrapper)

    await nextTick()
    await nextTick()

    return { trigger, wrapper }
  }

  it('enfoca el primer control interactivo al abrirse', async () => {
    const { wrapper } = await mountOpenModal({
      default: '<a href="/detalle">Ver detalle</a>',
    })

    expect(document.activeElement).toBe(document.querySelector('[role="dialog"] button'))
  })

  it('mantiene Tab y Shift+Tab dentro del diálogo', async () => {
    const { wrapper } = await mountOpenModal({
      default: '<button type="button">Acción</button>',
    })
    const buttons = document.querySelectorAll('[role="dialog"] button')
    const closeButton = buttons[0]
    const actionButton = buttons[1]

    actionButton.focus()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }))
    expect(document.activeElement).toBe(closeButton)

    closeButton.focus()
    document.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true })
    )
    expect(document.activeElement).toBe(actionButton)
  })

  it('devuelve el foco al elemento que abrió el modal al cerrarse', async () => {
    const { trigger, wrapper } = await mountOpenModal()

    await wrapper.setProps({ modelValue: false })
    await nextTick()

    expect(document.activeElement).toBe(trigger)
  })

  it('devuelve el foco al modal si se intenta enfocar un elemento detrás del overlay', async () => {
    const { wrapper } = await mountOpenModal({
      default: '<button type="button">Acción</button>',
    })
    const closeButton = document.querySelector('[role="dialog"] button')
    const outsideButton = document.createElement('button')
    outsideButton.textContent = 'Fuera del modal'
    document.body.appendChild(outsideButton)

    outsideButton.focus()

    expect(document.activeElement).toBe(closeButton)
  })
})
