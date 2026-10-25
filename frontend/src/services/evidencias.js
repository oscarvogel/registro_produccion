// Cliente de la API de evidencia fotografica (issue #204).
//
// La API vive en el backend desde el issue #198:
//   GET   /api/produccion/registros/{id}/evidencias  -> lista con estado
//   GET   /api/produccion/evidencias/{id}/archivo    -> los bytes de la foto
//   PATCH /api/produccion/evidencias/{id}             -> verificar / rechazar
//
// Las fotos se bajan con `responseType: 'blob'` porque el endpoint exige el
// token: un `<img src>` no lo manda y el servidor devolveria 401.
import api from '@/services/api'

export async function listarEvidencias(registroId) {
  const { data } = await api.get(`/api/produccion/registros/${registroId}/evidencias`, {
    _suppressErrorToast: true,
  })
  return Array.isArray(data) ? data : []
}

export async function descargarEvidencia(evidenciaId) {
  const { data } = await api.get(`/api/produccion/evidencias/${evidenciaId}/archivo`, {
    responseType: 'blob',
    _suppressErrorToast: true,
  })
  return data
}

/** Marca la foto como verificada (1) o rechazada (2), con el motivo. */
export async function verificarEvidencia(evidenciaId, { estado, comentario = '' } = {}) {
  const { data } = await api.patch(
    `/api/produccion/evidencias/${evidenciaId}`,
    { estado, comentario },
    { _suppressErrorToast: true },
  )
  return data
}
