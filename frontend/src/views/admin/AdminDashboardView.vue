<template>
  <div class="space-y-4">
    <section class="rounded-lg border border-neutral-200 bg-primary-dark p-5 text-white shadow-sm">
      <div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_34rem] xl:items-end">
        <div>
          <p class="text-xs font-bold uppercase tracking-wide text-primary-fixed-dim">Resumen ejecutivo</p>
          <h2 class="mt-1 text-2xl font-extrabold md:text-3xl">Dashboard de produccion</h2>
          <p class="mt-2 max-w-2xl text-sm text-primary-fixed-dim">
            Produccion total, toneladas, combustible y actividad operativa para el rango seleccionado.
          </p>
          <p class="mt-3 text-xs font-semibold text-primary-fixed-dim">
            Ultima actualizacion: {{ lastUpdatedLabel }} - Rango: {{ rangeLabel }}
          </p>
        </div>

        <div class="grid grid-cols-2 gap-2 md:grid-cols-4">
          <div
            v-for="item in executiveStats"
            :key="item.label"
            class="rounded-lg border border-white/15 bg-white/10 px-3 py-3"
          >
            <p class="text-[11px] font-bold uppercase tracking-wide text-primary-fixed-dim">{{ item.label }}</p>
            <p class="mt-1 text-xl font-extrabold text-white">{{ item.value }}</p>
            <p class="mt-0.5 text-[11px] text-primary-fixed-dim">{{ item.detail }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <div class="grid gap-4 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-end">
        <div>
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Filtros</p>
          <h3 class="mt-1 text-lg font-extrabold text-neutral-900">Periodo de analisis</h3>
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
                  ? 'border-secondary bg-secondary text-white'
                  : 'border-neutral-200 bg-neutral-50 text-neutral-600 hover:border-secondary/40',
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
            @click="loadOverview"
            class="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-primary-dark px-5 text-sm font-semibold text-white transition-colors hover:bg-primary disabled:opacity-60"
            :disabled="store.loadingDashboardOverview"
            type="button"
          >
            <AppIcon name="refresh" size="sm" :class="{ 'animate-spin': store.loadingDashboardOverview }" />
            Actualizar
          </button>
        </div>
      </div>
    </section>

    <div v-if="store.loadingDashboardOverview" class="rounded-lg border border-neutral-200 bg-white p-8 text-center text-neutral-500">
      Cargando resumen ejecutivo...
    </div>

    <div v-else-if="store.dashboardOverviewError" class="rounded-lg border border-error-light bg-error-light/40 p-4 text-sm font-semibold text-error-dark">
      {{ store.dashboardOverviewError }}
    </div>

    <div v-else-if="!overview" class="rounded-lg border border-neutral-200 bg-white p-10 text-center">
      <p class="font-bold text-neutral-700">No se pudo preparar el dashboard</p>
      <p class="mt-1 text-sm text-neutral-500">Actualiza el rango para volver a consultar la informacion.</p>
    </div>

    <template v-else>
      <section class="grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(22rem,0.65fr)]">
        <div class="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Produccion total</p>
              <div class="mt-2 flex flex-wrap items-end gap-x-3 gap-y-1">
                <span class="text-4xl font-extrabold text-neutral-950 md:text-5xl">
                  {{ formatNumber(totals.produccion_total) }}
                </span>
                <span class="pb-1 text-sm font-bold uppercase tracking-wide text-neutral-400">prod.</span>
              </div>
              <p class="mt-2 text-sm text-neutral-500">
                {{ formatNumber(totals.total_registros) }} registros - {{ formatNumber(totals.unidades_activas) }} unidades con actividad
              </p>
            </div>

            <div class="rounded-lg border px-3 py-2" :class="variationTone(primaryVariation)">
              <p class="text-[11px] font-bold uppercase tracking-wide">Periodo anterior</p>
              <p class="mt-1 text-xl font-extrabold">{{ variationLabel(primaryVariation) }}</p>
              <p class="text-xs">{{ previousRangeLabel }}</p>
            </div>
          </div>

          <div class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <div
              v-for="metric in metricCards"
              :key="metric.label"
              class="rounded-lg border border-neutral-200 bg-neutral-50 p-4"
            >
              <div class="flex items-center justify-between gap-3">
                <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">{{ metric.label }}</p>
                <AppIcon :name="metric.icon" size="sm" class="text-primary" />
              </div>
              <p class="mt-2 text-2xl font-extrabold text-neutral-900">{{ metric.value }}</p>
              <p class="mt-1 text-xs text-neutral-500">{{ metric.detail }}</p>
            </div>
          </div>
        </div>

        <aside class="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Comparativa</p>
          <h3 class="mt-1 text-lg font-extrabold text-neutral-900">Contra periodo anterior</h3>

          <div class="mt-4 divide-y divide-neutral-100">
            <div v-for="item in overview.variations" :key="item.key" class="py-3">
              <div class="flex items-center justify-between gap-3">
                <span class="text-sm font-bold text-neutral-700">{{ item.label }}</span>
                <span class="rounded-lg px-2 py-1 text-xs font-extrabold" :class="variationTone(item)">
                  {{ variationLabel(item) }}
                </span>
              </div>
              <div class="mt-1 flex items-center justify-between gap-3 text-xs text-neutral-400">
                <span>Actual {{ formatNumber(item.current) }}</span>
                <span>Anterior {{ formatNumber(item.previous) }}</span>
              </div>
            </div>
          </div>
        </aside>
      </section>

      <section class="grid gap-4 xl:grid-cols-[minmax(0,1.25fr)_minmax(22rem,0.75fr)]">
        <div class="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-end justify-between gap-3">
            <div>
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Evolucion diaria</p>
              <h3 class="mt-1 text-lg font-extrabold text-neutral-900">Produccion del periodo</h3>
            </div>
            <p class="text-xs font-semibold text-neutral-400">{{ overview.evolucion.length }} dias con datos</p>
          </div>

          <div v-if="chartPoints.length > 1" class="min-h-64">
            <svg :viewBox="`0 0 ${chartW} ${chartH}`" class="h-64 w-full" preserveAspectRatio="none">
              <line
                v-for="line in chartGrid"
                :key="line"
                :x1="chartPad"
                :x2="chartW - chartPad"
                :y1="line"
                :y2="line"
                stroke="var(--color-neutral-200)"
                stroke-width="1"
              />
              <polyline
                :points="linePoints"
                fill="none"
                stroke="var(--color-primary)"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="4"
              />
              <circle
                v-for="(point, index) in chartPoints"
                :key="`${point.x}-${index}`"
                :cx="point.x"
                :cy="point.y"
                r="4"
                fill="white"
                stroke="var(--color-primary-dark)"
                stroke-width="2"
              />
            </svg>
            <div class="mt-2 flex items-center justify-between text-xs font-semibold text-neutral-400">
              <span>{{ firstEvolutionDate }}</span>
              <span>{{ lastEvolutionDate }}</span>
            </div>
          </div>

          <div v-else class="flex h-64 items-center justify-center rounded-lg border border-dashed border-neutral-300 bg-neutral-50 text-sm text-neutral-500">
            Sin evolucion suficiente para graficar.
          </div>
        </div>

        <aside class="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Ranking</p>
          <h3 class="mt-1 text-lg font-extrabold text-neutral-900">Unidades por produccion</h3>

          <div v-if="overview.unidad_ranking.length > 0" class="mt-4 space-y-3">
            <div v-for="(item, index) in overview.unidad_ranking" :key="item.id || item.nombre">
              <div class="flex items-center justify-between gap-3">
                <div class="flex min-w-0 items-center gap-2">
                  <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-info-light text-xs font-extrabold text-info-dark">
                    {{ index + 1 }}
                  </span>
                  <div class="min-w-0">
                    <p class="truncate text-sm font-extrabold text-neutral-800">{{ item.nombre }}</p>
                    <p class="text-xs text-neutral-400">{{ formatNumber(item.registros) }} registros</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm font-extrabold text-neutral-900">{{ formatNumber(item.produccion) }}</p>
                  <p class="text-xs text-neutral-400">{{ formatNumber(item.share_percent) }}%</p>
                </div>
              </div>
              <div class="mt-2 h-2 overflow-hidden rounded-full bg-neutral-100">
                <div class="h-full rounded-full bg-primary" :style="{ width: `${Math.min(item.share_percent, 100)}%` }"></div>
              </div>
            </div>
          </div>

          <div v-else class="mt-4 rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-5 text-center text-sm text-neutral-500">
            Sin unidades con produccion en este periodo.
          </div>
        </aside>
      </section>

      <section class="grid gap-4 xl:grid-cols-2">
        <div class="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div class="mb-4">
            <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Procesos</p>
            <h3 class="mt-1 text-lg font-extrabold text-neutral-900">Produccion por proceso</h3>
          </div>

          <div v-if="overview.proceso_ranking.length > 0" class="overflow-hidden rounded-lg border border-neutral-200">
            <table class="w-full border-collapse text-left text-sm">
              <thead class="bg-neutral-50 text-xs uppercase tracking-wide text-neutral-400">
                <tr>
                  <th class="px-3 py-3 font-bold">Proceso</th>
                  <th class="px-3 py-3 text-right font-bold">Produccion</th>
                  <th class="px-3 py-3 text-right font-bold">TN</th>
                  <th class="px-3 py-3 text-right font-bold">Reg.</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-neutral-100">
                <tr v-for="item in overview.proceso_ranking" :key="item.id || item.nombre">
                  <td class="px-3 py-3 font-bold text-neutral-800">{{ item.nombre }}</td>
                  <td class="px-3 py-3 text-right font-extrabold text-info-dark">{{ formatNumber(item.produccion) }}</td>
                  <td class="px-3 py-3 text-right text-neutral-600">{{ formatNumber(item.tn_despachadas) }}</td>
                  <td class="px-3 py-3 text-right text-neutral-500">{{ formatNumber(item.registros) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-5 text-center text-sm text-neutral-500">
            Sin procesos con produccion en este periodo.
          </div>
        </div>

        <div class="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div class="mb-4">
            <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Actividad reciente</p>
            <h3 class="mt-1 text-lg font-extrabold text-neutral-900">Ultimos registros productivos</h3>
          </div>

          <div v-if="overview.recent_records.length > 0" class="space-y-2">
            <article
              v-for="record in overview.recent_records"
              :key="record.id"
              class="grid gap-3 rounded-lg border border-neutral-200 bg-neutral-50 px-3 py-3 md:grid-cols-[minmax(0,1fr)_auto] md:items-center"
            >
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="truncate text-sm font-extrabold text-neutral-800">{{ record.operacion || 'Sin operacion' }}</p>
                  <span class="rounded-md bg-white px-2 py-0.5 text-xs font-bold text-neutral-500">
                    {{ formatDate(record.fecha) }}
                  </span>
                </div>
                <p class="mt-1 truncate text-xs text-neutral-500">
                  {{ record.unidad || 'Sin unidad' }} - {{ record.equipo || 'Sin equipo' }} - {{ record.operador || 'Sin operador' }}
                </p>
              </div>
              <div class="text-sm md:text-right">
                <p class="font-extrabold text-info-dark">{{ formatNumber(record.produccion) }}</p>
                <p class="text-xs text-neutral-400">{{ formatNumber(record.combustible) }} L</p>
              </div>
            </article>
          </div>

          <div v-else class="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-5 text-center text-sm text-neutral-500">
            Sin registros recientes para el rango activo.
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import InputField from '@/components/InputField.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()

const rangePresets = [
  { key: 'today', label: 'Hoy' },
  { key: '7d', label: 'Ultimos 7 dias' },
  { key: '30d', label: 'Ultimos 30 dias' },
  { key: 'month', label: 'Este mes' },
]

const today = new Date()
const prior = new Date(today)
prior.setDate(prior.getDate() - 29)

const fechaDesde = ref(toYmd(prior))
const fechaHasta = ref(toYmd(today))
const activePreset = ref('30d')
const lastUpdated = ref(null)

const overview = computed(() => store.dashboardOverview)
const totals = computed(() => overview.value?.totals || emptyTotals())
const previousTotals = computed(() => overview.value?.previous_totals || emptyTotals())

const primaryVariation = computed(() => {
  return overview.value?.variations?.find((item) => item.key === 'produccion_total') || null
})

const executiveStats = computed(() => [
  {
    label: 'Produccion',
    value: formatNumber(totals.value.produccion_total),
    detail: variationLabel(primaryVariation.value),
  },
  {
    label: 'TN',
    value: formatNumber(totals.value.tn_despachadas_total),
    detail: 'Despachadas',
  },
  {
    label: 'Combustible',
    value: `${formatNumber(totals.value.combustible_total)} L`,
    detail: 'Consumo total',
  },
  {
    label: 'Registros',
    value: formatNumber(totals.value.total_registros),
    detail: 'Cargas del periodo',
  },
])

const metricCards = computed(() => [
  {
    label: 'TN despachadas',
    value: formatNumber(totals.value.tn_despachadas_total),
    detail: `${formatNumber(previousTotals.value.tn_despachadas_total)} en periodo anterior`,
    icon: 'truck',
  },
  {
    label: 'Combustible',
    value: `${formatNumber(totals.value.combustible_total)} L`,
    detail: `${formatNumber(previousTotals.value.combustible_total)} L en periodo anterior`,
    icon: 'fuel',
  },
  {
    label: 'Operadores',
    value: formatNumber(totals.value.operadores_activos),
    detail: 'Con registros en el rango',
    icon: 'personnel',
  },
  {
    label: 'Equipos',
    value: formatNumber(totals.value.equipos_activos),
    detail: 'Con actividad productiva',
    icon: 'machine',
  },
])

const rangeLabel = computed(() => `${formatDate(fechaDesde.value)} al ${formatDate(fechaHasta.value)}`)
const previousRangeLabel = computed(() => {
  if (!overview.value) return 'Sin periodo anterior'
  return `${formatDate(overview.value.periodo_anterior_desde)} al ${formatDate(overview.value.periodo_anterior_hasta)}`
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

const chartW = 640
const chartH = 220
const chartPad = 18
const chartGrid = [50, 100, 150, 200]

const maxProduction = computed(() => {
  const values = overview.value?.evolucion?.map((item) => Number(item.produccion || 0)) || []
  return Math.max(...values, 1)
})

const chartPoints = computed(() => {
  const rows = overview.value?.evolucion || []
  if (rows.length < 2) return []
  const usableW = chartW - chartPad * 2
  const usableH = chartH - chartPad * 2
  return rows.map((row, index) => ({
    x: chartPad + (index / (rows.length - 1)) * usableW,
    y: chartH - chartPad - (Number(row.produccion || 0) / maxProduction.value) * usableH,
  }))
})

const linePoints = computed(() => chartPoints.value.map((point) => `${point.x},${point.y}`).join(' '))
const firstEvolutionDate = computed(() => formatDate(overview.value?.evolucion?.[0]?.fecha))
const lastEvolutionDate = computed(() => {
  const rows = overview.value?.evolucion || []
  return formatDate(rows[rows.length - 1]?.fecha)
})

async function loadOverview() {
  activePreset.value = ''
  await fetchOverview()
}

async function applyPreset(key) {
  const now = new Date()
  const start = new Date(now)
  if (key === '7d') {
    start.setDate(now.getDate() - 6)
  } else if (key === '30d') {
    start.setDate(now.getDate() - 29)
  } else if (key === 'month') {
    start.setDate(1)
  }
  fechaDesde.value = toYmd(start)
  fechaHasta.value = toYmd(now)
  activePreset.value = key
  await fetchOverview()
}

async function fetchOverview() {
  await store.fetchDashboardOverview({
    fecha_desde: fechaDesde.value || null,
    fecha_hasta: fechaHasta.value || null,
  })
  lastUpdated.value = new Date()
}

function emptyTotals() {
  return {
    total_registros: 0,
    produccion_total: 0,
    tn_despachadas_total: 0,
    combustible_total: 0,
    unidades_activas: 0,
    operadores_activos: 0,
    equipos_activos: 0,
  }
}

function toYmd(value) {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
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

function variationLabel(item) {
  if (!item || item.variation_percent == null) return 'Sin base previa'
  const sign = Number(item.variation_percent) > 0 ? '+' : ''
  return `${sign}${formatNumber(item.variation_percent)}%`
}

function variationTone(item) {
  if (!item || item.variation_percent == null) return 'border-neutral-200 bg-neutral-50 text-neutral-500'
  if (Number(item.variation_percent) >= 0) return 'border-success-light bg-success-light/30 text-success-dark'
  return 'border-error-light bg-error-light/40 text-error-dark'
}

onMounted(() => {
  applyPreset('30d')
})
</script>
