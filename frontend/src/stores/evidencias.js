import { defineStore } from 'pinia'
import {
  descargarEvidencia,
  listarEvidencias,
  verificarEvidencia,
} from '@/services/evidencias'
import { ESTADO_PENDIENTE, ESTADO_RECHAZADA } from '@/utils/evidencia'

/**
 * Evidencia fotografica del registro que se esta revisando (issue #204).
 *
 * Las fotos se bajan del servidor y se muestran con object URLs: el endpoint
 * exige el token, asi que un `<img src>` pelado no llegaria a la foto. Las
 * URLs se liberan al limpiar el store (al cerrar el modal).
 */
export const useEvidenciasStore = defineStore('evidencias', {
  state: () => ({
    registroId: null,
    evidencias: [],
    urls: {},
    loading: false,
    error: null,
    accionEnCurso: null,
  }),

  getters: {
    tieneEvidencias: (state) => state.evidencias.length > 0,
    pendientes: (state) =>
      state.evidencias.filter((fila) => Number(fila.estado) === ESTADO_PENDIENTE),
    rechazadas: (state) =>
      state.evidencias.filter((fila) => Number(fila.estado) === ESTADO_RECHAZADA),
    estaVerificando: (state) => state.accionEnCurso !== null,
  },

  actions: {
    async cargar(registroId) {
      if (!registroId) {
        this.limpiar()
        return []
      }
      this.registroId = Number(registroId)
      this.loading = true
      this.error = null
      try {
        this.evidencias = await listarEvidencias(this.registroId)
        await this.cargarFotos()
        return this.evidencias
      } catch (err) {
        console.error('Error cargando la evidencia del registro:', err)
        this.error = 'No se pudieron cargar las fotos de evidencia'
        this.evidencias = []
        return []
      } finally {
        this.loading = false
      }
    },

    /** Baja los bytes de cada foto y arma la object URL para mostrar la miniatura. */
    async cargarFotos() {
      if (typeof URL?.createObjectURL !== 'function') return
      for (const fila of this.evidencias) {
        if (this.urls[fila.id]) continue
        try {
          const blob = await descargarEvidencia(fila.id)
          this.urls[fila.id] = URL.createObjectURL(blob)
        } catch (err) {
          console.error('Error bajando la foto de evidencia:', err)
        }
      }
    },

    /** Verifica o rechaza una foto y deja la lista actualizada. */
    async verificar(evidenciaId, { estado, comentario = '' }) {
      this.accionEnCurso = evidenciaId
      try {
        const actualizada = await verificarEvidencia(evidenciaId, { estado, comentario })
        this.evidencias = this.evidencias.map((fila) =>
          Number(fila.id) === Number(evidenciaId) ? { ...fila, ...actualizada } : fila,
        )
        return actualizada
      } finally {
        this.accionEnCurso = null
      }
    },

    limpiar() {
      if (typeof URL?.revokeObjectURL === 'function') {
        Object.values(this.urls).forEach((url) => {
          try {
            URL.revokeObjectURL(url)
          } catch {
            /* la URL ya no existe: no hay nada que liberar */
          }
        })
      }
      this.urls = {}
      this.evidencias = []
      this.registroId = null
      this.error = null
      this.loading = false
      this.accionEnCurso = null
    },
  },
})
