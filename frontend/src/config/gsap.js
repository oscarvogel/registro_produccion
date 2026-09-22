import { gsap } from 'gsap'
import { Flip } from 'gsap/Flip'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

let scrollTriggerRegistered = false

export function registerGsapPlugins() {
  gsap.registerPlugin(Flip)

  if (!scrollTriggerRegistered && typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    gsap.registerPlugin(ScrollTrigger)
    scrollTriggerRegistered = true
  }

  return scrollTriggerRegistered
}

registerGsapPlugins()

export const motionDurations = {
  micro: 0.18,
  enter: 0.32,
  list: 0.28,
  theme: 0.24,
}

export const motionEase = {
  standard: 'power2.out',
  settle: 'power3.out',
  spring: 'back.out(1.35)',
}

export function prefersReducedMotion() {
  return typeof window !== 'undefined'
    && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true
}

export function createMotionContext(root, setup) {
  return gsap.context(setup, root)
}

export function animateThemeIcon(target) {
  if (!target || prefersReducedMotion()) return null

  gsap.killTweensOf(target)
  gsap.set(target, { rotation: 0, scale: 1, transformOrigin: '50% 50%' })

  return gsap.timeline()
    .to(target, {
      rotation: 180,
      scale: 0.78,
      duration: motionDurations.micro,
      ease: 'power2.in',
    })
    .to(target, {
      rotation: 360,
      scale: 1,
      duration: motionDurations.micro + 0.08,
      ease: motionEase.spring,
    })
}

export function animateValidationTarget(target) {
  if (!target || prefersReducedMotion()) return null

  gsap.killTweensOf(target)
  return gsap.fromTo(
    target,
    { x: 0 },
    {
      x: 0,
      keyframes: [
        { x: -4, duration: 0.05 },
        { x: 4, duration: 0.05 },
        { x: -3, duration: 0.05 },
        { x: 3, duration: 0.05 },
        { x: 0, duration: 0.05 },
      ],
      ease: 'none',
    },
  )
}

export { Flip, ScrollTrigger, gsap }
