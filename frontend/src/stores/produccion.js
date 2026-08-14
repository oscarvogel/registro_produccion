import api from '@/services/api'
import db from '@/services/db'
import { ensurePendingIdentity, queuePendingProductionRecord } from '@/services/pendingRecords'
import { useToastStore } from '@/stores/toast'
import { extractApiErrorMessage, extractValidationErrorMessage } from '@/utils/apiError'
import { useProduccionStore as useLegacyProduccionStore } from '@/stores/produccionLegacy'

const CAMINOS_MARKER = '__submission_kind'
const CAMINOS_KIND = 'caminos'

const createFormUuid = () => (
  globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`
)

const isPermanentSyncError = (status) => (
  status >= 400 && status < 500 && ![401, 403, 408, 429].includes(status)
)

function withoutSyncMetadata(payload = {}) {
  const { [CAMINOS_MARKER]: _kind, ...clean } = payload
  return clean
}

function pendingEndpoint(payload = {}) {
  return payload?.[CAMINOS_MARKER] === CAMINOS_KIND
    ? '/api/produccion/caminos'
    : '/api/produccion/'
}

export function useProduccionStore(...args) {
  const store = useLegacyProduccionStore(...args)

  if (typeof store.submitParteCaminos === 'function') {
    return store
  }

  store.submitParteCaminos = async (formData) => {
    store.submitting = true
    store.error = null

    const payload = {
      ...formData,
      form_uuid: formData.form_uuid || createFormUuid(),
    }
    const pendingPayload = {
      ...payload,
      [CAMINOS_MARKER]: CAMINOS_KIND,
    }

    try {
      if (!navigator.onLine) {
        await queuePendingProductionRecord(pendingPayload)
        await store.refreshPendingCount()
        useToastStore().info(
          'Guardado solo en este teléfono',
          'El parte de Caminos quedó en Pendientes y se enviará cuando vuelva la conexión.',
        )
        return { offline: true, form_uuid: payload.form_uuid }
      }

      const { data } = await api.post('/api/produccion/caminos', payload)
      useToastStore().success('Parte de Caminos guardado')
      return data
    } catch (err) {
      if (!err.response) {
        await queuePendingProductionRecord(pendingPayload)
        await store.refreshPendingCount()
        useToastStore().info(
          'Guardado solo en este teléfono',
          'El servidor no confirmó la recepción. El parte permanece en Pendientes.',
        )
        return { offline: true, form_uuid: payload.form_uuid }
      }

      const isValidation = err.response?.status === 422
      const message = isValidation
        ? extractValidationErrorMessage(err, 'Revisá los procesos y datos obligatorios del parte de Caminos.')
        : extractApiErrorMessage(err, 'No se pudo guardar el parte de Caminos')
      store.error = message
      useToastStore().error('No se pudo guardar', message)
      throw err
    } finally {
      store.submitting = false
    }
  }

  // Reemplaza la sincronización legacy por una compatible con ambos contratos.
  // Los registros normales siguen enviándose al endpoint histórico y los partes
  // multi-proceso de Caminos se reenvían al endpoint específico.
  store.syncPending = async () => {
    if (store.syncingPending) {
      return { successCount: 0, pendingCount: store.pendingCount, permanentFailureCount: 0 }
    }

    store.syncingPending = true
    const pending = await db.pendingRecords.where('synced').equals(0).toArray()
    if (!pending.length) {
      store.syncingPending = false
      return { successCount: 0, pendingCount: 0, permanentFailureCount: 0 }
    }

    store.error = null
    let successCount = 0
    let permanentFailureCount = 0

    try {
      for (const record of pending) {
        try {
          await db.pendingRecords.update(record.id, {
            syncStatus: 'syncing',
            lastAttemptAt: Date.now(),
            retryCount: Number(record.retryCount || 0) + 1,
          })

          const identifiedPayload = await ensurePendingIdentity(record)
          const endpoint = pendingEndpoint(identifiedPayload)
          const submissionPayload = withoutSyncMetadata(identifiedPayload)

          await api.post(endpoint, submissionPayload, { _suppressErrorToast: true })
          await db.pendingRecords.delete(record.id)
          successCount++
        } catch (err) {
          const status = err?.response?.status
          if (isPermanentSyncError(status)) {
            const detail = extractApiErrorMessage(
              err,
              'Error permanente al sincronizar el registro',
            )
            await db.pendingRecords.update(record.id, {
              synced: 1,
              syncStatus: 'failed',
              syncError: detail,
              failedAt: Date.now(),
            })
            permanentFailureCount++
            continue
          }

          await db.pendingRecords.update(record.id, {
            synced: 0,
            syncStatus: 'pending',
            syncError: [401, 403].includes(status)
              ? 'La sesión debe validarse nuevamente antes de enviar.'
              : extractApiErrorMessage(
                  err,
                  'Error transitorio. Se reintentará automáticamente.',
                ),
          })
        }
      }

      await store.refreshPendingCount()
      if (permanentFailureCount > 0) {
        store.error = `No se pudieron sincronizar ${permanentFailureCount} registro(s) por un error permanente.`
        useToastStore().error('Sincronización parcial', store.error)
      } else if (successCount > 0) {
        useToastStore().success('Pendientes sincronizados', `${successCount} registro(s) enviados.`)
      }

      return {
        successCount,
        pendingCount: store.pendingCount,
        permanentFailureCount,
      }
    } finally {
      store.syncingPending = false
    }
  }

  return store
}
