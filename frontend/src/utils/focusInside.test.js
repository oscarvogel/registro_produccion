import { describe, it, expect, afterEach } from 'vitest'
import { focusInside } from './focusInside.js'

afterEach(() => {
  document.body.innerHTML = ''
})

describe('focusInside', () => {
  it('returns true when relatedTarget is inside the selector (real DOM)', () => {
    const dropdown = document.createElement('div')
    dropdown.setAttribute('data-moviles-dropdown', '')
    const item = document.createElement('button')
    item.setAttribute('data-moviles-item', '')
    dropdown.appendChild(item)
    document.body.appendChild(dropdown)

    const ev = { relatedTarget: item }
    expect(focusInside(ev, '[data-moviles-dropdown]')).toBe(true)
  })

  it('returns true when relatedTarget is the selector itself', () => {
    const dropdown = document.createElement('div')
    dropdown.setAttribute('data-moviles-dropdown', '')
    document.body.appendChild(dropdown)

    const ev = { relatedTarget: dropdown }
    expect(focusInside(ev, '[data-moviles-dropdown]')).toBe(true)
  })

  it('returns false when relatedTarget is outside the selector', () => {
    const dropdown = document.createElement('div')
    dropdown.setAttribute('data-moviles-dropdown', '')
    document.body.appendChild(dropdown)
    const outside = document.createElement('button')
    document.body.appendChild(outside)

    const ev = { relatedTarget: outside }
    expect(focusInside(ev, '[data-moviles-dropdown]')).toBe(false)
  })

  it('returns false when event is null', () => {
    expect(focusInside(null, '[data-moviles-dropdown]')).toBe(false)
  })

  it('returns false when relatedTarget is null (blur to nothing)', () => {
    const ev = { relatedTarget: null }
    expect(focusInside(ev, '[data-moviles-dropdown]')).toBe(false)
  })

  it('returns false when relatedTarget is undefined', () => {
    const ev = {}
    expect(focusInside(ev, '[data-moviles-dropdown]')).toBe(false)
  })

  it('returns false when selector is empty', () => {
    const ev = { relatedTarget: document.createElement('div') }
    expect(focusInside(ev, '')).toBe(false)
  })

  it('returns false when relatedTarget has no closest method', () => {
    const ev = { relatedTarget: {} }
    expect(focusInside(ev, '[data-moviles-dropdown]')).toBe(false)
  })
})
