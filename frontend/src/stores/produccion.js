import api from '@/services/api'
import db from '@/services/db'
import motivosNoOperativos from '@/data/motivosNoOperativos.json'
import {
  ensurePendingIdentity,
  pendingSubmissionEndpoint,
  queuePendingProductionRecord,
  stripPendingMetadata,
  SUBMISSION_KIND_FIELD,
  SUBMISSION_KIND_CAMINOS,
} from '@/services/pendingRecords'
import { useToastStore } from '@/stores/toast'
import { extractApiErrorMessage, extractValidationErrorMessage } from '@/utils/apiError'
import { useProduccionStore as useLegacyProduccionStore } from '@/stores/produccionLegacy'

const MOTIVOS_CACHE_PREFIX = 'motivosNoOperativos'

const createFormUuid = () => (
  globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`
)

const isPermanentSyncError = (status) => (
  status >= 400 && status < 500 && ![401, 403, 408, 429].includes(status)
)

function motivosCacheKey(unId) {
  return `${MOTIVOS_CACHE_PREFIX}:${Number(unId || 0)}`
}

function applyMotivos(items) {
  const nombres = (Array.isArray(items) ? items : [])
    .map((item) => String(item?.nombre ?? item ?? '').trim())
    .filter(Boolean)
  if (!nombres.length) return false
  motivosNoOperativos.splice(0, motivosNoOperativos.length, ...nombres)
  return true
}

async function fetchMotivosNoOperativos(unId) {
  if (!unId) return motivosNoOperativos
  try {
    const { data } = await api.get('/api/catalogos/motivos-no-operativos', {
      params: { un_id: Number(unId) },
      _suppressErrorToast: true,
    })
    if (Array.isArray(data)) {
      applyMotivos(data)
      if (db.catalogos) {
        await db.catalogos.put({
          key: motivosCacheKey(unId),
          catalog: MOTIVOS_CACHE_PREFIX,
          scope: String(unId),
          items: data,
          timestamp: Date.now(),
        })
      }
    }
  } catch (error) {
    if (db.catalogos) {
      const cached = await db.catalogos.get(motivosCacheKey(unId))
      if (cached?.items) applyMotivos(cached.items)
    }
  }
  return motivosNoOperativos
}

export function useProduccionStore(...args) {
  const store = useLegacyProduccionStore(...args)

  if (!store.__motivosNoOperativosCatalogReady) {
    const legacyFetchTiposProceso = store.fetchTiposProceso.bind(store)
    store.fetchTiposProceso = async (unId) => {
      const result = await legacyFetchTiposProceso(unId)
      await fetchMotivosNoOperativos(unId)
      return result
    }
    store.fetchMotivosNoOperativos = fetchMotivosNoOperativos
    store.__motivosNoOperativosCatalogReady = true
  }

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
      [SUBMISSION_KIND_FIELD]: SUBMISSION_KIND_CAMINOS,
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
      if (!err.response || Number(err.response?.status) >= 500) {
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
          const endpoint = pendingSubmissionEndpoint(identifiedPayload)
          const submissionPayload = stripPendingMetadata(identifiedPayload)

          await api.post(endpoint, submissionPayload, { _suppressErrorToast: true })
          await db.pendingRecords.delete(record.id)
          successCount++
        } catch (err) {
          const status = err?.response?.status
          if (isPermanentSyncError(status)) {
            const detail = extractApiErrorMessage(err, 'Error permanente al sincronizar el registro')
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
              : extractApiErrorMessage(err, 'Error transitorio. Se reintentará automáticamente.'),
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

      return { successCount, pendingCount: store.pendingCount, permanentFailureCount }
    } finally {
      store.syncingPending = false
    }
  }

  return store
}
