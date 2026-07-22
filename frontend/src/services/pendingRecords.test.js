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
import { ensurePendingIdentity, queuePendingProductionRecord } from './pendingRecords'

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
})
