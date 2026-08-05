import { describe, expect, it } from 'vitest'

import { isCanonicalRemito, normalizeRemito } from './remito'

describe('normalizeRemito', () => {
  it.each([
    ['1', '000000000001'],
    ['11278', '000000011278'],
    ['011278', '000000011278'],
    ['000000011278', '000000011278'],
    ['21325', '000000021325'],
    ['0', '000000000000'],
    ['999999999999', '999999999999'],
  ])('padds el remito numerico %s a %s', (entrada, esperado) => {
    expect(normalizeRemito(entrada)).toBe(esperado)
  })

  it.each([
    ['R-0001', 'R-0001'],
    ['r-0001', 'R-0001'],
    ['D000001', 'D000001'],
    ['A-1', 'A-1'],
  ])('conserva el remito alfanumerico %s tal cual (en mayusculas)', (entrada, esperado) => {
    expect(normalizeRemito(entrada)).toBe(esperado)
  })

  it('elimina espacios al principio y al final', () => {
    expect(normalizeRemito('  11278  ')).toBe('000000011278')
    expect(normalizeRemito(' R-0001 ')).toBe('R-0001')
  })

  it('devuelve string vacio para entrada vacia', () => {
    expect(normalizeRemito('')).toBe('')
    expect(normalizeRemito('   ')).toBe('')
  })

  it('devuelve null para entrada null/undefined', () => {
    expect(normalizeRemito(null)).toBeNull()
    expect(normalizeRemito(undefined)).toBeNull()
  })

  it('devuelve null si el remito tiene caracteres invalidos', () => {
    expect(normalizeRemito('11.278')).toBeNull()
    expect(normalizeRemito('11 278')).toBeNull()
    expect(normalizeRemito('11/278')).toBeNull()
    expect(normalizeRemito('R.0001')).toBeNull()
  })

  it('devuelve null si el remito numerico tiene mas de 12 digitos', () => {
    expect(normalizeRemito('1234567890123')).toBeNull()
  })

  it('devuelve null si el remito alfanumerico tiene mas de 12 caracteres', () => {
    expect(normalizeRemito('R-00012345678')).toBeNull()
  })
})

describe('isCanonicalRemito', () => {
  it('devuelve true para valores ya normalizados', () => {
    expect(isCanonicalRemito('000000011278')).toBe(true)
    expect(isCanonicalRemito('R-0001')).toBe(true)
  })

  it('devuelve false para valores sin normalizar', () => {
    expect(isCanonicalRemito('11278')).toBe(false)
    expect(isCanonicalRemito('11.278')).toBe(false)
  })

  it('devuelve false para valores vacios o nulos', () => {
    expect(isCanonicalRemito('')).toBe(false)
    expect(isCanonicalRemito(null)).toBe(false)
    expect(isCanonicalRemito(undefined)).toBe(false)
  })
})
