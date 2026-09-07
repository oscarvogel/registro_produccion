import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/db', () => ({
  default: {
    pendingRecords: {
      add: vi.fn(async () => 1),
      update: vi.fn(async () => 1),
    },
  },
}))

import db from '@/services/db'
import {
  ensurePendingIdentity,
  pendingSubmissionEndpoint,
  queuePendingProductionRecord,
  stripPendingMetadata,
  SUBMISSION_KIND_FIELD,
  SUBMISSION_KIND_CAMINOS,
  SUBMISSION_KIND_COMBUSTIBLE,
} from './pendingRecords'

describe('pending production records', () => {
  beforeEach(() => vi.clearAllMocks())

  it('uses form_uuid as the stable local client id', async () => {
    await queuePendingProductionRecord({ fecha: '2026-07-21', form_uuid: 'form-123' })

    expect(db.pendingRecords.add).toHaveBeenCalledWith(expect.objectContaining({
      clientId: 'form-123',
      payload: expect.objectContaining({ form_uuid: 'form-123' }),
    }))
  })

  it('persists an identity for a v1 record before retrying it', async () => {
    const payload = await ensurePendingIdentity({
      id: 9,
      payload: { fecha: '2026-07-21' },
    })

    expect(payload.form_uuid).toBeTruthy()
    expect(db.pendingRecords.update).toHaveBeenCalledWith(9, expect.objectContaining({
      clientId: payload.form_uuid,
      payload,
    }))
  })

  it('routes each queued kind to its correct endpoint and strips local metadata', () => {
    expect(pendingSubmissionEndpoint({})).toBe('/api/produccion/')
    expect(pendingSubmissionEndpoint({ [SUBMISSION_KIND_FIELD]: SUBMISSION_KIND_CAMINOS })).toBe('/api/produccion/caminos')
    expect(pendingSubmissionEndpoint({ [SUBMISSION_KIND_FIELD]: SUBMISSION_KIND_COMBUSTIBLE })).toBe('/api/combustible/cargas')
    expect(stripPendingMetadata({ form_uuid: 'x', [SUBMISSION_KIND_FIELD]: SUBMISSION_KIND_COMBUSTIBLE })).toEqual({ form_uuid: 'x' })
  })
})
