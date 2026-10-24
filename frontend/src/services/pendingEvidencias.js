import db from '@/services/db'

// Cola offline de las fotos de evidencia (decision D3, issue #202).
//
// La foto se toma antes de que exista el parte, asi que se guarda sola con el
// `form_uuid` del formulario. Cuando vuelve la senal, el sync sube PRIMERO
// las fotos y DESPUES el parte: si la foto no sube, el parte no se envia
// (el backend rechaza un parte sin la evidencia que su tipo de proceso exige).

const OFFLINE_SCHEMA_VERSION = 4

export async function queuePendingEvidencia({
  formUuid,
  tipo,
  blob,
  incluyeHorometro = false,
  nombre = 'evidencia.jpg',
}) {
  return db.pendingEvidencias.add({
    formUuid,
    tipo,
    blob,
    incluyeHorometro: incluyeHorometro ? 1 : 0,
    nombre,
    schemaVersion: OFFLINE_SCHEMA_VERSION,
    timestamp: Date.now(),
    synced: 0,
    syncStatus: 'pending',
    retryCount: 0,
  })
}

// Fotos encoladas de un formulario, en el orden en que se sacaron.
export async function listarEvidenciasPendientes(formUuid) {
  if (!formUuid) return []
  const filas = await db.pendingEvidencias.where('formUuid').equals(formUuid).toArray()
  return filas.sort((a, b) => a.id - b.id)
}

export async function contarEvidenciasPendientes() {
  return db.pendingEvidencias.where('synced').equals(0).count()
}

export async function marcarEvidenciaSincronizada(id) {
  return db.pendingEvidencias.update(id, {
    synced: 1,
    syncStatus: 'synced',
    syncedAt: Date.now(),
  })
}

export async function marcarEvidenciaConError(id, mensaje) {
  return db.pendingEvidencias.update(id, {
    synced: 0,
    syncStatus: 'pending',
    syncError: mensaje,
  })
}

export async function eliminarEvidenciasDeFormulario(formUuid) {
  if (!formUuid) return 0
  return db.pendingEvidencias.where('formUuid').equals(formUuid).delete()
}
