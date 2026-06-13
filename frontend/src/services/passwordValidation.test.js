import { describe, expect, it } from 'vitest'

import {
  ADMIN_PASSWORD_TOO_LONG_MESSAGE,
  passwordByteLength,
  validateAdminPassword,
} from './passwordValidation'

describe('validateAdminPassword', () => {
  it('accepts empty passwords so editing a person keeps the existing password', () => {
    expect(validateAdminPassword()).toBe('')
    expect(validateAdminPassword('')).toBe('')
  })

  it('accepts passwords up to 72 bytes', () => {
    expect(passwordByteLength('a'.repeat(72))).toBe(72)
    expect(validateAdminPassword('a'.repeat(72))).toBe('')
  })

  it('rejects passwords longer than 72 bytes with a user-facing message', () => {
    expect(validateAdminPassword('a'.repeat(73))).toBe(ADMIN_PASSWORD_TOO_LONG_MESSAGE)
    expect(ADMIN_PASSWORD_TOO_LONG_MESSAGE).not.toMatch(/bcrypt|passlib|bytes|truncate/i)
  })

  it('counts utf-8 bytes before hashing', () => {
    const password = 'ñ'.repeat(37)

    expect(passwordByteLength(password)).toBe(74)
    expect(validateAdminPassword(password)).toBe(ADMIN_PASSWORD_TOO_LONG_MESSAGE)
  })
})
