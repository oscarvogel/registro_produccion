import { nextTick, onBeforeUnmount, watch } from 'vue'
import { Flip, motionDurations, motionEase, prefersReducedMotion } from '@/config/gsap'

export function useGsapFlipList({ container, source, itemSelector = '[data-flip-id]' } = {}) {
  let flipAnimation = null

  const stop = watch(
    source,
    async () => {
      if (prefersReducedMotion() || !container?.value) return

      const beforeItems = container.value.querySelectorAll(itemSelector)
      if (beforeItems.length === 0) return

      const state = Flip.getState(beforeItems)
      await nextTick()

      const afterItems = container.value?.querySelectorAll(itemSelector)
      if (!afterItems?.length) return

      flipAnimation?.kill?.()
      flipAnimation = Flip.from(state, {
        targets: afterItems,
        duration: motionDurations.list,
        ease: motionEase.standard,
        stagger: 0.02,
        absolute: false,
      })
    },
    { deep: true, flush: 'pre' },
  )

  onBeforeUnmount(() => {
    stop()
    flipAnimation?.kill?.()
    flipAnimation = null
  })

  return {
    stop,
  }
}
