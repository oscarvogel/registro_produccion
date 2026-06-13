import { describe, expect, it } from 'vitest'

import { SERVER_ERROR_MESSAGE, normalizeBaseURL } from './api'

describe('normalizeBaseURL', () => {
  it('uses relative URLs when no base URL is configured', () => {
    expect(normalizeBaseURL()).toBe('')
    expect(normalizeBaseURL('')).toBe('')
  })

  it('removes a trailing api segment from configured base URLs', () => {
    expect(normalizeBaseURL('/api')).toBe('')
    expect(normalizeBaseURL('/api/')).toBe('')
    expect(normalizeBaseURL('https://example.com/api')).toBe('https://example.com')
  })

  it('keeps non-api base URLs unchanged', () => {
    expect(normalizeBaseURL('http://localhost:8000')).toBe('http://localhost:8000')
  })
})

describe('server error toast message', () => {
  it('uses a generic message instead of backend details for 5xx errors', () => {
    const technicalDetail = `
      pymysql.err.OperationalError: (2013, 'Lost connection to MySQL server during query')
      SELECT id, dni, password_hash FROM usuarios WHERE dni = %s
    `

    expect(SERVER_ERROR_MESSAGE).toBe('No se pudo conectar con el servidor. Intenta nuevamente en unos minutos.')
    expect(SERVER_ERROR_MESSAGE).not.toContain(technicalDetail)
    expect(SERVER_ERROR_MESSAGE).not.toMatch(/pymysql|OperationalError|SELECT|usuarios|password_hash/i)
  })
})
