<template>
  <AppModal
    :model-value="modelValue"
    :title="titulo"
    :description="descripcion"
    @update:model-value="(value) => emit('update:modelValue', value)"
  >
    <div v-if="loading" class="flex justify-center py-10" data-testid="record-detail-loading">
      <div class="h-8 w-8 animate-spin rounded-full border-3 border-primary border-t-transparent"></div>
    </div>

    <div
      v-else-if="error"
      class="rounded-lg border border-error/30 bg-error-light/40 p-4 text-sm text-error-dark"
      data-testid="record-detail-error"
    >
      {{ error }}
    </div>

    <div v-else-if="detalle" class="space-y-4" data-testid="record-detail-content">
      <section
        v-for="grupo in gruposVisibles"
        :key="grupo.titulo"
        class="rounded-lg border border-neutral-200 p-3"
      >
        <h4 class="mb-2 text-xs font-extrabold uppercase tracking-wide text-neutral-500">
          {{ grupo.titulo }}
        </h4>
        <dl class="grid grid-cols-1 gap-x-4 gap-y-1.5 sm:grid-cols-2">
          <div v-for="campo in grupo.campos" :key="campo.key" class="flex flex-col">
            <dt class="text-[11px] font-semibold uppercase text-neutral-400">{{ campo.label }}</dt>
            <dd class="text-sm font-semibold text-neutral-900">{{ formatCampo(detalle[campo.key], campo) }}</dd>
          </div>
        </dl>
      </section>

      <!-- Evidencia fotografica (issue #204): la seccion donde el encargado
           contrasta la foto y decide si la acepta. -->
      <section
        v-if="evidenciasStore.tieneEvidencias || evidenciasStore.loading"
        class="rounded-lg border border-neutral-200 p-3"
        data-testid="record-detail-evidencia"
      >
        <h4 class="mb-2 text-xs font-extrabold uppercase tracking-wide text-neutral-500">
          Evidencia fotográfica
        </h4>

        <p v-if="evidenciasStore.loading" class="text-sm text-neutral-500">
          Cargando las fotos...
        </p>

        <p v-else-if="evidenciasStore.error" class="text-sm font-semibold text-error-dark">
          {{ evidenciasStore.error }}
        </p>

        <div v-else class="space-y-3">
          <article
            v-for="evidencia in evidenciasStore.evidencias"
            :key="evidencia.id"
            class="rounded-lg border border-neutral-200 p-2.5"
            :data-testid="`evidencia-${evidencia.id}`"
          >
            <div class="flex gap-3">
              <img
                v-if="evidenciasStore.urls[evidencia.id]"
                :src="evidenciasStore.urls[evidencia.id]"
                :alt="rolLabel(evidencia.tipo)"
                class="h-24 w-24 shrink-0 rounded-lg border border-neutral-200 object-cover"
                data-testid="evidencia-foto"
              />
              <div
                v-else
                class="flex h-24 w-24 shrink-0 items-center justify-center rounded-lg border border-dashed border-neutral-300 px-1 text-center text-[11px] font-semibold text-neutral-500"
              >
                Sin vista previa
              </div>

              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="text-sm font-bold text-neutral-900">{{ rolLabel(evidencia.tipo) }}</span>
                  <AppBadge :tone="estadoTone(evidencia.estado)">
                    {{ estadoLabel(evidencia.estado) }}
                  </AppBadge>
                </div>

                <!-- Aviso de la declaracion D7: el operador dijo que el
                     horometro se ve en esta pantalla. El encargado lo
                     contrasta con la foto delante. -->
                <p
                  v-if="mostraDeclaracion(evidencia)"
                  class="mt-1.5 rounded-md bg-warning-light px-2 py-1.5 text-xs font-semibold text-warning-dark"
                  data-testid="evidencia-declaracion"
                >
                  El operador declaró que el horómetro se ve en esta pantalla. Revisá la foto: si el
                  horómetro no se ve, rechazala con el motivo.
                </p>

                <p v-if="evidencia.verificado_por" class="mt-1.5 text-xs text-neutral-500">
                  {{ Number(evidencia.estado) === ESTADO_RECHAZADA ? 'Rechazada' : 'Verificada' }} por
                  {{ evidencia.verificado_por }}
                  <span v-if="evidencia.verificado_at"> · {{ formatFechaHora(evidencia.verificado_at) }}</span>
                </p>

                <p
                  v-if="evidencia.comentario"
                  class="mt-1 text-xs font-semibold text-error-dark"
                  data-testid="evidencia-motivo"
                >
                  Motivo: {{ evidencia.comentario }}
                </p>

                <div
                  v-if="puedeVerificar && Number(evidencia.estado) === ESTADO_PENDIENTE"
                  class="mt-2 flex flex-wrap gap-2"
                >
                  <AppButton
                    size="sm"
                    variant="primary"
                    :loading="evidenciasStore.accionEnCurso === evidencia.id"
                    :data-testid="`verificar-${evidencia.id}`"
                    @click="verificar(evidencia)"
                  >
                    Verificar
                  </AppButton>
                  <AppButton
                    size="sm"
                    variant="danger"
                    :disabled="evidenciasStore.accionEnCurso !== null"
                    :data-testid="`rechazar-${evidencia.id}`"
                    @click="rechazar(evidencia)"
                  >
                    Rechazar
                  </AppButton>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>

    <template v-if="!loading && detalle" #actions>
      <div class="flex flex-wrap items-center justify-end gap-2 border-t border-neutral-200 px-4 py-3">
        <span class="text-[11px] text-neutral-400">ID #{{ detalle.id }}</span>
      </div>
    </template>
  </AppModal>
</template>

<script setup>
import { computed, watch } from 'vue'
import Swal from 'sweetalert2'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardRegistrosStore } from '@/stores/dashboardRegistros'
import { useEvidenciasStore } from '@/stores/evidencias'
import { useToastStore } from '@/stores/toast'
import {
  ESTADO_PENDIENTE,
  ESTADO_RECHAZADA,
  ESTADO_VERIFICADA,
  ROL_PROCESADOR,
  estadoLabel,
  estadoTone,
  rolLabel,
} from '@/utils/evidencia'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  registroId: { type: [Number, null], default: null },
})

const emit = defineEmits(['update:modelValue'])

const store = useDashboardRegistrosStore()
const authStore = useAuthStore()
const evidenciasStore = useEvidenciasStore()
const toast = useToastStore()

const detalle = computed(() => store.detalle)
const loading = computed(() => store.detalleLoading)
const error = computed(() => store.detalleError)

// Verificar y rechazar es del encargado (D-D): el operador no puede.
const puedeVerificar = computed(
  () => authStore.isAdmin === true || Number(authStore.user?.encargado || 0) === 1,
)

const titulo = computed(() => {
  if (!detalle.value) return 'Detalle del registro'
  const fecha = formatFecha(detalle.value.fecha)
  const operacion = detalle.value.operacion || 'Produccion'
  return `${operacion} - ${fecha}`
})

const descripcion = computed(() => {
  if (!detalle.value) return ''
  const equipo = detalle.value.equipo || 'Sin equipo'
  const operador = detalle.value.operador || 'Sin operador'
  return `${operador} - ${equipo}`
})

/** Devuelve true si el valor se considera "vacio" y debe ocultarse del modal. */
function campoVacio(valor) {
  return valor === null || valor === undefined || valor === '' || valor === '0' || valor === 0
}

/** Filtra los grupos para mostrar solo los campos con dato cargado.
 *  Si un grupo queda sin campos visibles, tambien se oculta. */
const gruposVisibles = computed(() => {
  if (!detalle.value) return []
  return grupos
    .map((grupo) => ({
      ...grupo,
      campos: grupo.campos.filter((campo) => !campoVacio(detalle.value[campo.key])),
    }))
    .filter((grupo) => grupo.campos.length > 0)
})

const grupos = [
  {
    titulo: 'Identificacion',
    campos: [
      { key: 'UN', label: 'Unidad de negocio' },
      { key: 'operacion', label: 'Operacion' },
      { key: 'fecha', label: 'Fecha', tipo: 'fecha' },
      { key: 'operador', label: 'Operador' },
      { key: 'equipo', label: 'Equipo' },
      { key: 'usuario', label: 'Cargado por' },
    ],
  },
  {
    titulo: 'Horómetros y operación',
    campos: [
      { key: 'hr_inicio', label: 'Horómetro inicial', tipo: 'numero' },
      { key: 'hr_fin', label: 'Horómetro final', tipo: 'numero' },
      { key: 'hr_disposicion', label: 'Horas disposicion', tipo: 'numero' },
      { key: 'hrs_no_op', label: 'Horas no operativas', tipo: 'numero' },
      { key: 'motivo_no_op', label: 'Motivo no operativo' },
      { key: 'servicio_tercero', label: 'Servicio tercero', tipo: 'booleano' },
      { key: 'detalle_servicio', label: 'Detalle servicio' },
    ],
  },
  {
    titulo: 'Produccion',
    campos: [
      { key: 'produccion', label: 'Produccion', tipo: 'numero' },
      { key: 'unidad_produccion', label: 'Unidad' },
      { key: 'unitario', label: 'Unitario', tipo: 'numero' },
      { key: 'tn_despachadas', label: 'Toneladas', tipo: 'numero' },
      { key: 'm3', label: 'm3', tipo: 'numero' },
      { key: 'has', label: 'Hectareas', tipo: 'numero' },
      { key: 'carros', label: 'Carros', tipo: 'numero' },
      { key: 'plantas', label: 'Plantas', tipo: 'numero' },
      { key: 'km_carreteo', label: 'KM carreteo', tipo: 'numero' },
      { key: 'km_perfilado', label: 'KM perfilado', tipo: 'numero' },
      { key: 'mtrs_recorridos', label: 'Metros recorridos', tipo: 'numero' },
      { key: 'dist_tosquera', label: 'Distancia tosquera', tipo: 'numero' },
      { key: 'viaje_tosca', label: 'Viaje tosca', tipo: 'numero' },
    ],
  },
  {
    titulo: 'Consumos',
    campos: [
      { key: 'combustible', label: 'Combustible (lts)', tipo: 'numero' },
      { key: 'aceite_cadena', label: 'Aceite cadena', tipo: 'numero' },
      { key: 'aceite_hidraulico', label: 'Aceite hidraulico', tipo: 'numero' },
      { key: 'aceite_motor', label: 'Aceite motor', tipo: 'numero' },
      { key: 'aceite_embrague', label: 'Aceite embrague', tipo: 'numero' },
      { key: 'aceite_transmision', label: 'Aceite transmision', tipo: 'numero' },
    ],
  },
  {
    titulo: 'Ubicacion y referencia',
    campos: [
      { key: 'predio', label: 'Predio' },
      { key: 'acta', label: 'Acta' },
      { key: 'rodal', label: 'Rodal' },
      { key: 'parcela', label: 'Parcela' },
      { key: 'lugar_carga', label: 'Lugar de carga', tipo: 'numero' },
    ],
  },
  {
    titulo: 'Remitos de combustible',
    campos: [
      { key: 'remito', label: 'Remito 1' },
      { key: 'remito2', label: 'Remito 2' },
      { key: 'remito3', label: 'Remito 3' },
      { key: 'remito_bitren', label: 'Remito bitren' },
      { key: 'remito_proveedor', label: 'Remito proveedor' },
      { key: 'remito_fgpy', label: 'Remito FGPY' },
    ],
  },
  {
    titulo: 'Observaciones',
    campos: [{ key: 'observaciones', label: 'Notas' }],
  },
]

function formatCampo(valor, campo) {
  if (valor === null || valor === undefined || valor === '' || valor === '0' || valor === 0) {
    return '-'
  }
  if (campo.tipo === 'fecha') return formatFecha(valor)
  if (campo.tipo === 'numero') return formatNumero(valor)
  if (campo.tipo === 'booleano') return Number(valor) === 1 ? 'Si' : 'No'
  return valor
}

function formatFecha(fecha) {
  if (!fecha) return '-'
  const str = String(fecha)
  const [y, m, d] = str.split('-')
  if (y && m && d) return `${d}/${m}/${y}`
  return str
}

function formatNumero(valor) {
  const n = Number(valor)
  if (!Number.isFinite(n)) return '-'
  if (Number.isInteger(n)) return n.toLocaleString('es-AR')
  return n.toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 2 })
}

/** La foto del procesador con la declaracion D7: el horometro se ve en ella. */
function mostraDeclaracion(evidencia) {
  return (
    evidencia.tipo === ROL_PROCESADOR && Number(evidencia.incluye_horometro || 0) === 1
  )
}

function formatFechaHora(valor) {
  if (!valor) return ''
  const fecha = new Date(valor)
  if (Number.isNaN(fecha.getTime())) return String(valor)
  return fecha.toLocaleString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function verificar(evidencia) {
  try {
    await evidenciasStore.verificar(evidencia.id, {
      estado: ESTADO_VERIFICADA,
      comentario: '',
    })
    toast.success('Foto verificada', 'La evidencia quedó aceptada por el encargado.')
  } catch (err) {
    toast.error('No se pudo verificar la foto', 'Intentá de nuevo en unos minutos.')
  }
}

async function rechazar(evidencia) {
  const { value } = await Swal.fire({
    icon: 'warning',
    title: 'Rechazar la foto',
    input: 'text',
    inputPlaceholder: 'Por ejemplo: el horómetro no se ve en la pantalla',
    inputValidator: (motivo) =>
      String(motivo || '').trim().length >= 5
        ? true
        : 'Contá el motivo del rechazo (por lo menos 5 letras).',
    showCancelButton: true,
    confirmButtonText: 'Rechazar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#3d935d',
  })
  if (!value) return
  try {
    await evidenciasStore.verificar(evidencia.id, {
      estado: ESTADO_RECHAZADA,
      comentario: String(value).trim(),
    })
    toast.info('Foto rechazada', 'El registro queda observado: el operador puede subir otra foto.')
  } catch (err) {
    toast.error('No se pudo rechazar la foto', 'Intentá de nuevo en unos minutos.')
  }
}

watch(
  () => [props.modelValue, props.registroId],
  async ([open, id]) => {
    if (open && id) {
      await store.fetchDetalle(id)
      // El detalle dice cuantas fotos hay: si no hay evidencia, no se pide la
      // lista (la mayoria de los registros no tienen fotos).
      const total = Number(store.detalle?.evidencias_total || 0)
      if (total > 0) {
        await evidenciasStore.cargar(id)
      } else {
        evidenciasStore.limpiar()
      }
    } else if (!open) {
      store.clearDetalle()
      evidenciasStore.limpiar()
    }
  },
  { immediate: true },
)
</script>
