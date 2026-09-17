import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import {
  animateThemeIcon,
  createMotionContext,
  prefersReducedMotion,
  registerGsapPlugins,
} from './gsap'

const originalMatchMedia = Object.getOwnPropertyDescriptor(window, 'matchMedia')

describe('GSAP motion helpers', () => {
  afterEach(() => {
    if (originalMatchMedia) Object.defineProperty(window, 'matchMedia', originalMatchMedia)
    else delete window.matchMedia
  })

  it('does not require matchMedia to load the core helpers', () => {
    delete window.matchMedia
    expect(registerGsapPlugins()).toBe(false)
    expect(prefersReducedMotion()).toBe(false)
  })

  it('detects reduced motion and skips the icon timeline', () => {
    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      value: () => ({ matches: true }),
    })
    const target = document.createElement('span')

    expect(prefersReducedMotion()).toBe(true)
    expect(animateThemeIcon(target)).toBeNull()
  })

  it('creates an icon timeline when motion is allowed', () => {
    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      value: () => ({ matches: false }),
    })
    const target = document.createElement('span')

    const animation = animateThemeIcon(target)

    expect(animation).toBeTruthy()
    animation.kill()
  })

  it('creates a revertible scoped context', () => {
    const root = document.createElement('div')
    const context = createMotionContext(root, () => {})

    expect(context).toHaveProperty('revert')
    context.revert()
  })
})
