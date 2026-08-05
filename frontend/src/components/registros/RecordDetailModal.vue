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
        v-for="grupo in grupos"
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
import AppModal from '@/components/ui/AppModal.vue'
import { useDashboardRegistrosStore } from '@/stores/dashboardRegistros'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  registroId: { type: [Number, null], default: null },
})

const emit = defineEmits(['update:modelValue'])

const store = useDashboardRegistrosStore()

const detalle = computed(() => store.detalle)
const loading = computed(() => store.detalleLoading)
const error = computed(() => store.detalleError)

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
    titulo: 'Horario y operacion',
    campos: [
      { key: 'hr_inicio', label: 'Hora inicio', tipo: 'hora' },
      { key: 'hr_fin', label: 'Hora fin', tipo: 'hora' },
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
  if (campo.tipo === 'hora') return formatHora(valor)
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

function formatHora(valor) {
  const n = Number(valor)
  if (!Number.isFinite(n) || n === 0) return '-'
  return n.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function formatNumero(valor) {
  const n = Number(valor)
  if (!Number.isFinite(n)) return '-'
  if (Number.isInteger(n)) return n.toLocaleString('es-AR')
  return n.toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 2 })
}

watch(
  () => [props.modelValue, props.registroId],
  async ([open, id]) => {
    if (open && id) {
      await store.fetchDetalle(id)
    } else if (!open) {
      store.clearDetalle()
    }
  },
  { immediate: true },
)
</script>
