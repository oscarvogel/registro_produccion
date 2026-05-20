<template>
  <div class="space-y-5">
    <section class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Resumen general del sistema</p>
          <h2 class="mt-1 text-2xl font-extrabold text-primary-dark">Panel de Administracion</h2>
          <p class="mt-1 text-sm text-neutral-500">
            Controla usuarios, unidades de negocio, permisos y metricas operativas.
          </p>
          <p class="mt-2 text-xs text-neutral-400">
            Ultima actualizacion: {{ lastUpdatedLabel }} - Rango activo: {{ rangeLabel }}
          </p>
        </div>

        <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:w-[34rem]">
          <div
            v-for="item in globalSummary"
            :key="item.label"
            class="rounded-xl border border-neutral-200 bg-neutral-50 px-3 py-2.5"
          >
            <p class="text-[11px] font-bold uppercase tracking-wide text-neutral-400">{{ item.label }}</p>
            <p class="mt-1 text-xl font-extrabold text-neutral-900">{{ item.value }}</p>
            <p class="text-[11px] text-neutral-400">{{ item.detail }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
      <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Dashboard operativo</p>
          <h2 class="mt-1 text-xl font-extrabold text-primary-dark">Metricas por unidad de negocio</h2>
        </div>

        <div class="flex flex-col gap-3 lg:flex-row lg:items-end">
          <div class="flex flex-wrap gap-2">
            <button
              v-for="preset in rangePresets"
              :key="preset.key"
              @click="applyPreset(preset.key)"
              :class="[
                'rounded-lg border px-3 py-2 text-xs font-bold transition-colors',
                activePreset === preset.key
                  ? 'border-primary-dark bg-primary-dark text-white'
                  : 'border-neutral-200 bg-neutral-50 text-neutral-600 hover:border-primary/40',
              ]"
              type="button"
            >
              {{ preset.label }}
            </button>
          </div>

          <div class="grid grid-cols-2 gap-2 sm:w-[24rem]">
            <InputField v-model="fechaDesde" type="date" label="Desde" />
            <InputField v-model="fechaHasta" type="date" label="Hasta" />
          </div>

          <button
            @click="loadDashboard"
            class="h-12 rounded-xl bg-primary-dark px-5 text-sm font-semibold text-white transition-colors hover:bg-primary"
            type="button"
          >
            Actualizar
          </button>
        </div>
      </div>
    </section>

    <div v-if="store.loading" class="rounded-2xl border border-neutral-200 bg-white p-8 text-center text-neutral-500">
      Cargando dashboard de administracion...
    </div>

    <div v-else-if="store.error" class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ store.error }}
    </div>

    <div v-else-if="store.dashboard.length === 0" class="rounded-2xl border border-neutral-200 bg-white p-10 text-center">
      <p class="font-bold text-neutral-700">No hay unidades para mostrar</p>
      <p class="mt-1 text-sm text-neutral-500">Cuando existan unidades activas, apareceran en este panel.</p>
    </div>

    <template v-else>
      <section v-if="!selectedUnidad" class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_22rem]">
        <div class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
          <div class="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Gestion del sistema</p>
              <h3 class="text-lg font-extrabold text-neutral-900">Unidades de negocio</h3>
            </div>
            <select
              v-model="selectedMetricKey"
              class="rounded-xl border border-neutral-300 bg-neutral-50 px-3 py-2 text-sm text-neutral-800 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              <option v-for="metric in visibleMetricOptions" :key="metric.key" :value="metric.key">
                Visualizar: {{ metric.label }}
              </option>
            </select>
          </div>

          <div class="divide-y divide-neutral-100">
            <article
              v-for="unidad in pagedUnits"
              :key="unidad.id"
              class="grid gap-4 py-4 lg:grid-cols-[minmax(13rem,0.8fr)_minmax(0,1fr)_auto] lg:items-center"
            >
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <h4 class="truncate text-base font-extrabold text-primary-dark">{{ unidad.nombre }}</h4>
                  <span class="rounded-md bg-neutral-100 px-2 py-0.5 text-xs font-bold text-neutral-500">{{ unidad.prefijo || 'SIN' }}</span>
                </div>
                <p class="mt-1 text-xs text-neutral-400">
                  {{ unidad.tipos_proceso.length }} proceso{{ unidad.tipos_proceso.length !== 1 ? 's' : '' }} configurado{{ unidad.tipos_proceso.length !== 1 ? 's' : '' }}
                </p>
              </div>

              <div v-if="hasUnitData(unidad)" class="grid gap-2 sm:grid-cols-3">
                <div class="rounded-xl bg-neutral-50 px-3 py-2">
                  <p class="text-[11px] font-bold uppercase tracking-wide text-neutral-400">Registros</p>
                  <p class="text-lg font-extrabold text-neutral-900">{{ formatNumber(unidad.resumen.total_registros) }}</p>
                </div>
                <div class="rounded-xl bg-neutral-50 px-3 py-2">
                  <p class="text-[11px] font-bold uppercase tracking-wide text-neutral-400">{{ selectedMetric.label }}</p>
                  <p class="text-lg font-extrabold text-neutral-900">{{ formatNumber(metricValue(unidad, selectedMetric.key)) }}</p>
                </div>
                <div class="rounded-xl bg-neutral-50 px-3 py-2">
                  <p class="text-[11px] font-bold uppercase tracking-wide text-neutral-400">Activos</p>
                  <p class="text-lg font-extrabold text-neutral-900">{{ unidad.resumen.operadores_activos }} / {{ unidad.resumen.equipos_activos }}</p>
                </div>
              </div>

              <div v-else class="rounded-xl border border-dashed border-neutral-300 bg-neutral-50 px-4 py-3">
                <p class="text-sm font-bold text-neutral-700">Sin registros en este periodo</p>
                <p class="mt-0.5 text-xs text-neutral-400">Cuando se cargue produccion para esta unidad, apareceran los indicadores principales.</p>
              </div>

              <button
                @click="openUnidad(unidad.id)"
                class="rounded-xl border border-primary/30 px-4 py-2 text-sm font-bold text-primary-dark transition-colors hover:bg-primary/5"
                type="button"
              >
                Ver detalle
              </button>
            </article>
          </div>

          <div v-if="unitTotalPages > 1" class="mt-4 flex flex-col gap-3 border-t border-neutral-100 pt-4 sm:flex-row sm:items-center sm:justify-between">
            <p class="text-xs font-semibold text-neutral-400">
              Mostrando {{ unitPageStart + 1 }}-{{ unitPageEnd }} de {{ sortedUnits.length }} unidades
            </p>
            <div class="flex items-center gap-2">
              <button
                @click="unitPage = Math.max(1, unitPage - 1)"
                :disabled="unitPage === 1"
                class="rounded-lg border border-neutral-200 px-3 py-2 text-xs font-bold text-neutral-600 disabled:opacity-40"
                type="button"
              >
                Anterior
              </button>
              <span class="rounded-lg bg-neutral-100 px-3 py-2 text-xs font-extrabold text-neutral-700">
                {{ unitPage }} / {{ unitTotalPages }}
              </span>
              <button
                @click="unitPage = Math.min(unitTotalPages, unitPage + 1)"
                :disabled="unitPage === unitTotalPages"
                class="rounded-lg border border-neutral-200 px-3 py-2 text-xs font-bold text-neutral-600 disabled:opacity-40"
                type="button"
              >
                Siguiente
              </button>
            </div>
          </div>
        </div>

        <aside class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Dashboard operativo</p>
          <h3 class="mt-1 text-lg font-extrabold text-neutral-900">Procesos configurados</h3>
          <div class="mt-4 space-y-3">
            <div
              v-for="process in processSummary"
              :key="process.nombre"
              class="rounded-xl bg-neutral-50 px-3 py-2"
            >
              <div class="flex items-center justify-between gap-3">
                <p class="truncate text-sm font-bold text-neutral-800">{{ process.nombre }}</p>
                <span class="rounded-md bg-white px-2 py-0.5 text-xs font-bold text-neutral-500">{{ process.unidades }}</span>
              </div>
              <p class="mt-1 text-xs text-neutral-400">{{ formatNumber(process.registros) }} registros - {{ formatNumber(process.produccion) }} produccion</p>
            </div>
          </div>
        </aside>
      </section>

      <section v-else class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
        <div class="mb-5 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <button
              @click="selectedUnidadId = null"
              class="mb-3 text-sm font-bold text-primary-dark hover:text-primary"
              type="button"
            >
              Volver a unidades
            </button>
            <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Detalle de unidad</p>
            <h3 class="mt-1 text-2xl font-extrabold text-primary-dark">{{ selectedUnidad.nombre }}</h3>
            <p class="mt-1 text-sm text-neutral-500">Procesos y metricas disponibles para {{ selectedUnidad.prefijo || 'esta unidad' }}.</p>
          </div>

          <div class="grid gap-2 sm:grid-cols-2 lg:w-[28rem]">
            <select
              v-model="selectedProcessId"
              class="h-11 rounded-xl border border-neutral-300 bg-neutral-50 px-3 text-sm text-neutral-800 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              <option value="all">Todos los procesos</option>
              <option v-for="tipo in selectedUnidad.tipos_proceso" :key="tipo.id" :value="String(tipo.id)">
                {{ tipo.nombre }}
              </option>
            </select>
            <select
              v-model="selectedMetricKey"
              class="h-11 rounded-xl border border-neutral-300 bg-neutral-50 px-3 text-sm text-neutral-800 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              <option v-for="metric in unitMetricOptions" :key="metric.key" :value="metric.key">
                {{ metric.label }}
              </option>
            </select>
          </div>
        </div>

        <div v-if="!hasUnitData(selectedUnidad)" class="rounded-2xl border border-dashed border-neutral-300 bg-neutral-50 p-8 text-center">
          <p class="text-base font-extrabold text-neutral-700">Sin registros en este periodo</p>
          <p class="mt-1 text-sm text-neutral-500">Cuando se cargue produccion para esta unidad, apareceran los indicadores principales.</p>
        </div>

        <div v-else class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div class="space-y-5">
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div
                v-for="metric in selectedUnitStats"
                :key="metric.label"
                class="rounded-xl bg-neutral-50 p-4"
              >
                <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">{{ metric.label }}</p>
                <p class="mt-2 text-2xl font-extrabold text-neutral-900">{{ metric.value }}</p>
                <p class="mt-1 text-xs text-neutral-400">{{ metric.detail }}</p>
              </div>
            </div>

            <div>
              <p class="mb-3 text-xs font-bold uppercase tracking-wide text-neutral-400">Tipos de proceso</p>
              <div class="space-y-2">
                <div
                  v-for="tipo in filteredProcesses"
                  :key="`${selectedUnidad.id}-${tipo.id}`"
                  class="grid gap-3 rounded-xl border border-neutral-200 px-4 py-3 md:grid-cols-[minmax(0,1fr)_8rem_8rem] md:items-center"
                >
                  <div class="min-w-0">
                    <p class="truncate text-sm font-extrabold text-neutral-800">{{ tipo.nombre }}</p>
                    <p class="text-xs text-neutral-400">{{ tipo.registros }} registro{{ tipo.registros !== 1 ? 's' : '' }}</p>
                  </div>
                  <div class="text-sm">
                    <span class="block text-xs font-bold uppercase tracking-wide text-neutral-400">Produccion</span>
                    <span class="font-extrabold text-primary-dark">{{ formatNumber(tipo.produccion) }}</span>
                  </div>
                  <div class="h-2 rounded-full bg-neutral-100">
                    <div class="h-full rounded-full bg-primary" :style="{ width: `${processShare(tipo)}%` }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <aside class="rounded-2xl bg-neutral-50 p-5">
            <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Indicadores</p>
            <div class="mt-4 divide-y divide-neutral-200">
              <div
                v-for="row in selectedUnitRows"
                :key="row.label"
                class="flex items-center justify-between gap-4 py-3"
              >
                <span class="text-sm text-neutral-500">{{ row.label }}</span>
                <span class="text-sm font-extrabold text-neutral-900">{{ row.value }}</span>
              </div>
            </div>
          </aside>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import InputField from '@/components/InputField.vue'
import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()

const rangePresets = [
  { key: 'today', label: 'Hoy' },
  { key: '7d', label: 'Ultimos 7 dias' },
  { key: '30d', label: 'Ultimos 30 dias' },
  { key: 'month', label: 'Este mes' },
]

function toYmd(value) {
  return value.toISOString().slice(0, 10)
}

const today = new Date()
const prior = new Date(today)
prior.setDate(prior.getDate() - 29)

const fechaDesde = ref(toYmd(prior))
const fechaHasta = ref(toYmd(today))
const activePreset = ref('30d')
const lastUpdated = ref(null)
const selectedUnidadId = ref(null)
const selectedMetricKey = ref('produccion_total')
const selectedProcessId = ref('all')
const unitPage = ref(1)
const UNITS_PER_PAGE = 6

const metricOptions = [
  { key: 'produccion_total', label: 'Produccion total' },
  { key: 'tn_despachadas_total', label: 'TN despachadas' },
  { key: 'combustible_total', label: 'Combustible' },
  { key: 'total_registros', label: 'Total registros' },
  { key: 'registros_hoy', label: 'Registros hoy' },
]

const selectedMetric = computed(() => {
  return metricOptions.find((metric) => metric.key === selectedMetricKey.value) || metricOptions[0]
})

const visibleMetricOptions = computed(() => {
  const hasTn = store.dashboard.some((unidad) => Number(unidad.resumen?.tn_despachadas_total || 0) > 0)
  const hasProduction = store.dashboard.some((unidad) => Number(unidad.resumen?.produccion_total || 0) > 0)
  const hasFuel = store.dashboard.some((unidad) => Number(unidad.resumen?.combustible_total || 0) > 0)
  return metricOptions.filter((metric) => {
    if (metric.key === 'tn_despachadas_total') return hasTn
    if (metric.key === 'produccion_total') return hasProduction || !hasTn
    if (metric.key === 'combustible_total') return hasFuel
    return true
  })
})

const unitMetricOptions = computed(() => {
  if (!selectedUnidad.value) return visibleMetricOptions.value
  return metricOptions.filter((metric) => {
    if (['total_registros', 'registros_hoy'].includes(metric.key)) return true
    return Number(metricValue(selectedUnidad.value, metric.key)) > 0
  })
})

const selectedUnidad = computed(() => {
  return store.dashboard.find((unidad) => Number(unidad.id) === Number(selectedUnidadId.value)) || null
})

const sortedUnits = computed(() => {
  return [...store.dashboard].sort((a, b) => {
    const left = Number(a.resumen?.total_registros || 0)
    const right = Number(b.resumen?.total_registros || 0)
    if (right !== left) return right - left
    return String(a.nombre || '').localeCompare(String(b.nombre || ''))
  })
})

const unitTotalPages = computed(() => Math.max(1, Math.ceil(sortedUnits.value.length / UNITS_PER_PAGE)))
const unitPageStart = computed(() => (unitPage.value - 1) * UNITS_PER_PAGE)
const unitPageEnd = computed(() => Math.min(unitPageStart.value + UNITS_PER_PAGE, sortedUnits.value.length))
const pagedUnits = computed(() => sortedUnits.value.slice(unitPageStart.value, unitPageEnd.value))

const globalTotals = computed(() => {
  return store.dashboard.reduce((acc, unidad) => {
    const resumen = unidad.resumen || {}
    acc.total_registros += Number(resumen.total_registros || 0)
    acc.registros_hoy += Number(resumen.registros_hoy || 0)
    acc.produccion_total += Number(resumen.produccion_total || 0)
    acc.tn_despachadas_total += Number(resumen.tn_despachadas_total || 0)
    acc.combustible_total += Number(resumen.combustible_total || 0)
    acc.operadores_activos += Number(resumen.operadores_activos || 0)
    acc.equipos_activos += Number(resumen.equipos_activos || 0)
    return acc
  }, {
    total_registros: 0,
    registros_hoy: 0,
    produccion_total: 0,
    tn_despachadas_total: 0,
    combustible_total: 0,
    operadores_activos: 0,
    equipos_activos: 0,
  })
})

const globalSummary = computed(() => [
  { label: 'Total registros', value: formatNumber(globalTotals.value.total_registros), detail: 'Periodo activo' },
  { label: 'Produccion', value: formatNumber(globalTotals.value.produccion_total), detail: 'Total general' },
  { label: 'Combustible', value: `${formatNumber(globalTotals.value.combustible_total)} L`, detail: 'Consumo total' },
  { label: 'Unidades', value: formatNumber(store.dashboard.length), detail: 'Activas' },
])

const processSummary = computed(() => {
  const map = new Map()
  for (const unidad of store.dashboard) {
    for (const tipo of unidad.tipos_proceso || []) {
      const current = map.get(tipo.nombre) || { nombre: tipo.nombre, unidades: 0, registros: 0, produccion: 0 }
      current.unidades += 1
      current.registros += Number(tipo.registros || 0)
      current.produccion += Number(tipo.produccion || 0)
      map.set(tipo.nombre, current)
    }
  }
  return [...map.values()].sort((a, b) => b.registros - a.registros).slice(0, 8)
})

const filteredProcesses = computed(() => {
  if (!selectedUnidad.value) return []
  if (selectedProcessId.value === 'all') return selectedUnidad.value.tipos_proceso || []
  return (selectedUnidad.value.tipos_proceso || []).filter((tipo) => String(tipo.id) === selectedProcessId.value)
})

const selectedUnitStats = computed(() => {
  if (!selectedUnidad.value) return []
  const unidad = selectedUnidad.value
  return [
    {
      label: selectedMetric.value.label,
      value: formatNumber(metricValue(unidad, selectedMetric.value.key)),
      detail: 'Metrica seleccionada',
    },
    {
      label: 'Registros',
      value: formatNumber(unidad.resumen.total_registros),
      detail: `${formatNumber(unidad.resumen.registros_hoy)} hoy`,
    },
    {
      label: 'Operadores / Equipos',
      value: `${unidad.resumen.operadores_activos} / ${unidad.resumen.equipos_activos}`,
      detail: 'Con actividad en el rango',
    },
  ]
})

const selectedUnitRows = computed(() => {
  if (!selectedUnidad.value) return []
  const resumen = selectedUnidad.value.resumen
  return [
    { label: 'Total registros', value: formatNumber(resumen.total_registros) },
    { label: 'Registros hoy', value: formatNumber(resumen.registros_hoy) },
    { label: 'Produccion total', value: formatNumber(resumen.produccion_total) },
    { label: 'TN despachadas', value: formatNumber(resumen.tn_despachadas_total) },
    { label: 'Combustible', value: `${formatNumber(resumen.combustible_total)} L` },
    { label: 'Operadores / Equipos', value: `${resumen.operadores_activos} / ${resumen.equipos_activos}` },
  ].filter((row) => !row.value.startsWith('0') || ['Total registros', 'Registros hoy'].includes(row.label))
})

const rangeLabel = computed(() => {
  return `${formatDate(fechaDesde.value)} al ${formatDate(fechaHasta.value)}`
})

const lastUpdatedLabel = computed(() => {
  if (!lastUpdated.value) return 'sin actualizar'
  return new Intl.DateTimeFormat('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(lastUpdated.value)
})

watch(unitMetricOptions, (options) => {
  if (options.length > 0 && !options.some((metric) => metric.key === selectedMetricKey.value)) {
    selectedMetricKey.value = options[0].key
  }
})

watch(unitTotalPages, (totalPages) => {
  if (unitPage.value > totalPages) {
    unitPage.value = totalPages
  }
})

async function loadDashboard() {
  activePreset.value = ''
  unitPage.value = 1
  await store.fetchDashboard({
    fecha_desde: fechaDesde.value || null,
    fecha_hasta: fechaHasta.value || null,
  })
  lastUpdated.value = new Date()
  if (selectedUnidadId.value && !selectedUnidad.value) {
    selectedUnidadId.value = null
  }
}

async function applyPreset(key) {
  const now = new Date()
  const start = new Date(now)
  if (key === 'today') {
    // same date
  } else if (key === '7d') {
    start.setDate(now.getDate() - 6)
  } else if (key === '30d') {
    start.setDate(now.getDate() - 29)
  } else if (key === 'month') {
    start.setDate(1)
  }
  fechaDesde.value = toYmd(start)
  fechaHasta.value = toYmd(now)
  activePreset.value = key
  unitPage.value = 1
  await store.fetchDashboard({
    fecha_desde: fechaDesde.value,
    fecha_hasta: fechaHasta.value,
  })
  lastUpdated.value = new Date()
}

function openUnidad(id) {
  selectedUnidadId.value = id
  selectedProcessId.value = 'all'
}

function hasUnitData(unidad) {
  return Number(unidad.resumen?.total_registros || 0) > 0
}

function metricValue(unidad, key) {
  return Number(unidad?.resumen?.[key] || 0)
}

function processShare(tipo) {
  const total = filteredProcesses.value.reduce((sum, item) => sum + Number(item.produccion || 0), 0)
  if (total <= 0) return tipo.registros > 0 ? 100 : 0
  return Math.max(4, Math.round((Number(tipo.produccion || 0) / total) * 100))
}

function formatNumber(value) {
  const numeric = Number(value || 0)
  return numeric.toLocaleString('es-AR', { maximumFractionDigits: 2 })
}

function formatDate(value) {
  if (!value) return '-'
  const [year, month, day] = String(value).split('-')
  if (!year || !month || !day) return value
  return `${day}/${month}/${year}`
}

onMounted(() => {
  applyPreset('30d')
})
</script>
