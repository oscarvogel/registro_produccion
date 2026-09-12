import { mount } from '@vue/test-utils'
import AppPreloader from './AppPreloader.vue'

describe('AppPreloader', () => {
  it('announces a route loading state', () => {
    const wrapper = mount(AppPreloader, { props: { label: 'Cargando operación...' } })

    expect(wrapper.attributes('role')).toBe('status')
    expect(wrapper.text()).toContain('Cargando operación...')
  })
})
