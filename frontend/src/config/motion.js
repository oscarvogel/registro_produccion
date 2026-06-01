const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

const standardTransition = prefersReducedMotion
  ? { duration: 0 }
  : { type: 'spring', stiffness: 360, damping: 32, mass: 0.7 }

export const motionPluginOptions = {
  directives: {
    page: {
      initial: prefersReducedMotion ? { opacity: 1 } : { opacity: 0, y: 10 },
      enter: { opacity: 1, y: 0, transition: standardTransition },
    },
    panel: {
      initial: prefersReducedMotion ? { opacity: 1 } : { opacity: 0, y: 8 },
      visibleOnce: { opacity: 1, y: 0, transition: standardTransition },
    },
    pop: {
      initial: prefersReducedMotion ? { opacity: 1 } : { opacity: 0, scale: 0.98, y: 6 },
      enter: { opacity: 1, scale: 1, y: 0, transition: standardTransition },
    },
  },
}
