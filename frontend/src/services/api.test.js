import { describe, expect, it } from 'vitest'

import { normalizeBaseURL } from './api'

describe('normalizeBaseURL', () => {
  it('removes a trailing api segment from configured base URLs', () => {
    expect(normalizeBaseURL('/api')).toBe('')
    expect(normalizeBaseURL('/api/')).toBe('')
    expect(normalizeBaseURL('https://example.com/api')).toBe('https://example.com')
  })

  it('keeps non-api base URLs unchanged', () => {
    expect(normalizeBaseURL('http://localhost:8000')).toBe('http://localhost:8000')
  })
})
