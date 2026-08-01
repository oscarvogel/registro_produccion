import { describe, expect, it } from 'vitest'

import {
  extractApiErrorMessage,
  extractValidationErrorMessage,
  normalizeProduccionPayload,
} from './apiError'

describe('extractApiErrorMessage', () => {
  it('returns a backend-provided string detail as-is', () => {
    const error = {
      response: {
        status: 422,
        data: { detail: 'El combustible requiere un kilometraje u horometro mayor a cero' },
      },
    }

    expect(extractApiErrorMessage(error)).toBe(
      'El combustible requiere un kilometraje u horometro mayor a cero',
    )
  })

  it('strips the Pydantic "Value error, " prefix from value_error entries', () => {
    const error = {
      response: {
        status: 422,
        data: {
          detail: [
            {
              type: 'value_error',
              loc: ['body'],
              msg: 'Value error, El combustible requiere un kilometraje u horometro mayor a cero',
              input: {},
            },
          ],
        },
      },
    }

    expect(extractApiErrorMessage(error)).toBe(
      'El combustible requiere un kilometraje u horometro mayor a cero',
    )
  })

  it('translates the raw int_parsing Pydantic error into a friendly sentence', () => {
    const error = {
      response: {
        status: 422,
        data: {
          detail: [
            {
              type: 'int_parsing',
              loc: ['body', 'aceite_hidraulico'],
              msg: 'Input should be a valid integer, unable to parse string as an integer',
              input: '',
              url: 'https://errors.pydantic.dev/2.13/v/int_parsing',
            },
          ],
        },
      },
    }

    const message = extractApiErrorMessage(error)
    expect(message).toBe('uno de los campos numericos no es un numero valido')
    expect(message).not.toContain('Input should be')
    expect(message).not.toContain('errors.pydantic.dev')
  })

  it('never leaks URLs, input payloads or internal field paths to the operator', () => {
    const error = {
      response: {
        status: 422,
        data: {
          detail: [
            {
              type: 'int_parsing',
              loc: ['body', 'aceite_hidraulico'],
              msg: 'Input should be a valid integer, unable to parse string as an integer',
              input: { secret: 'should-not-leak', password: 'hidden' },
              url: 'https://errors.pydantic.dev/2.13/v/int_parsing',
            },
          ],
        },
      },
    }

    const message = extractApiErrorMessage(error)
    expect(message).not.toContain('should-not-leak')
    expect(message).not.toContain('hidden')
    expect(message).not.toContain('errors.pydantic.dev')
    expect(message).not.toContain('aceite_hidraulico')
  })

  it('falls back to a generic Spanish message for unknown shapes', () => {
    const error = { response: { status: 500, data: { something: 'weird' } } }
    expect(extractApiErrorMessage(error)).toBe(
      'No se pudo completar la operacion. Intenta nuevamente en unos minutos.',
    )
  })

  it('falls back to a generic message when the request never reached the server', () => {
    const error = { message: 'Network Error' }
    expect(extractApiErrorMessage(error)).toBe(
      'No se pudo completar la operacion. Intenta nuevamente en unos minutos.',
    )
  })

  it('honours a custom fallback when provided', () => {
    const error = { response: { status: 500, data: {} } }
    expect(extractApiErrorMessage(error, 'algo salio mal')).toBe('algo salio mal')
  })
})

describe('extractValidationErrorMessage', () => {
  it('uses the validation fallback for 422 responses that carry no useful detail', () => {
    const error = { response: { status: 422, data: {} } }
    expect(extractValidationErrorMessage(error)).toBe(
      'Los datos enviados no son validos. Revisa los campos del formulario e intenta nuevamente.',
    )
  })

  it('uses the validation fallback when the error is empty', () => {
    expect(extractValidationErrorMessage(null)).toBe(
      'Los datos enviados no son validos. Revisa los campos del formulario e intenta nuevamente.',
    )
  })

  it('returns the backend-provided string detail for 422', () => {
    const error = {
      response: {
        status: 422,
        data: { detail: 'El combustible requiere un lugar de carga' },
      },
    }
    expect(extractValidationErrorMessage(error)).toBe(
      'El combustible requiere un lugar de carga',
    )
  })
})

describe('normalizeProduccionPayload', () => {
  it('coerces empty-string numeric fields to 0', () => {
    const payload = {
      fecha: '2026-07-31',
      aceite_hidraulico: '',
      aceite_motor: '',
      hr_inicio: 100,
    }

    const result = normalizeProduccionPayload(payload)

    expect(result.aceite_hidraulico).toBe(0)
    expect(result.aceite_motor).toBe(0)
    expect(result.hr_inicio).toBe(100)
    expect(result.fecha).toBe('2026-07-31')
  })

  it('coerces null numeric fields to 0', () => {
    const payload = {
      fecha: '2026-07-31',
      aceite_hidraulico: null,
      combustible: null,
      km_combustible: null,
    }

    const result = normalizeProduccionPayload(payload)

    expect(result.aceite_hidraulico).toBe(0)
    expect(result.combustible).toBe(0)
    expect(result.km_combustible).toBe(0)
  })

  it('treats whitespace-only strings as empty', () => {
    const payload = { aceite_hidraulico: '   ' }
    expect(normalizeProduccionPayload(payload).aceite_hidraulico).toBe(0)
  })

  it('leaves real numeric values untouched', () => {
    const payload = {
      aceite_hidraulico: 5,
      hr_inicio: 1335.6,
      combustible: 137,
    }

    const result = normalizeProduccionPayload(payload)

    expect(result.aceite_hidraulico).toBe(5)
    expect(result.hr_inicio).toBe(1335.6)
    expect(result.combustible).toBe(137)
  })

  it('does not touch unknown or non-numeric fields', () => {
    const payload = {
      fecha: '2026-07-31',
      operacion: 'HORAS MAQUINAS',
      observaciones: '',
      acta: '',
    }

    const result = normalizeProduccionPayload(payload)

    expect(result.operacion).toBe('HORAS MAQUINAS')
    expect(result.observaciones).toBe('')
    expect(result.acta).toBe('')
  })

  it('returns the original reference when payload is not a plain object', () => {
    expect(normalizeProduccionPayload(null)).toBeNull()
    expect(normalizeProduccionPayload(undefined)).toBeUndefined()
    expect(normalizeProduccionPayload('hello')).toBe('hello')
  })

  it('does not mutate the input payload', () => {
    const payload = { aceite_hidraulico: '' }
    const result = normalizeProduccionPayload(payload)
    expect(payload.aceite_hidraulico).toBe('')
    expect(result).not.toBe(payload)
  })
})
