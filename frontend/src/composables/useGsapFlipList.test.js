import { defineComponent, nextTick, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Flip } from '@/config/gsap'
import { useGsapFlipList } from './useGsapFlipList'

describe('useGsapFlipList', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('captures and animates items through stable data-flip-id values', async () => {
    const capturedIds = []
    vi.spyOn(Flip, 'getState').mockImplementation((elements) => {
      capturedIds.push(Array.from(elements).map((element) => element.dataset.flipId))
      return {}
    })
    vi.spyOn(Flip, 'from').mockReturnValue({ kill: vi.fn() })

    const Harness = defineComponent({
      setup() {
        const source = ref([{ id: 'a' }, { id: 'b' }])
        const container = ref(null)
        useGsapFlipList({ container, source: () => source.value })
        return { source, container }
      },
      template: `
        <div ref="container">
          <div v-for="item in source" :key="item.id" :data-flip-id="` + "'item-'" + ` + item.id"></div>
        </div>
      `,
    })

    const wrapper = mount(Harness)
    wrapper.vm.source = [{ id: 'b' }, { id: 'a' }]
    await nextTick()
    await nextTick()

    expect(capturedIds).toEqual([['item-a', 'item-b']])
    expect(Flip.from).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ duration: expect.any(Number) }),
    )

    wrapper.unmount()
  })
})
