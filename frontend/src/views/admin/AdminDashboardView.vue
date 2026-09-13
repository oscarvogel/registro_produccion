<template>
  <div class="min-w-0 space-y-3">
    <section class="min-w-0 rounded-lg border border-white/20 bg-primary-dark p-4 text-white shadow-sm" aria-labelledby="admin-dashboard-title">
      <div class="grid gap-3 xl:grid-cols-[minmax(0,1fr)_34rem] xl:items-end">
        <div>
          <p class="text-xs font-bold uppercase tracking-wide text-white/90">Análisis gerencial</p>
          <h2 id="admin-dashboard-title" class="mt-1 text-2xl font-extrabold md:text-3xl">Análisis de Producción</h2>
          <p class="mt-2 max-w-2xl text-sm text-white/90">
            Análisis productivo y gerencial de producción total, toneladas, combustible y actividad para el rango seleccionado.
          </p>
          <p class="mt-3 text-xs font-semibold text-white/90">
            Última actualización: {{ lastUpdatedLabel }} - Alcance: Todas las unidades de negocio - Rango: {{ rangeLabel }}
          </p>
        </div>
      </div>
    </section>

    <section class="app-card min-w-0 rounded-lg p-3.5">
      <div class="grid gap-3 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-end">
        <div>
          <p class="text-xs font-bold uppercase tracking-wide text-[var(--app-text-soft)]">Filtros</p>
          <h3 class="mt-1 text-lg font-extrabold text-[var(--app-text)]">Periodo de análisis</h3>
        </div>

        <div class="flex flex-col gap-2.5 lg:flex-row lg:items-end">
          <div class="flex flex-wrap gap-2">
            <button
              v-for="preset in rangePresets"
              :key="preset.key"
              @click="applyPreset(preset.key)"
              :aria-pressed="activePreset === preset.key"
              :class="[
                'rounded-lg border px-3 py-2 text-xs font-bold transition-colors',
                activePreset === preset.key
                  ? 'border-secondary bg-secondary text-on-secondary'
                  : 'app-button-soft border',
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

          <AppButton :loading="store.loadingDashboardOverview" :disabled="store.loadingDashboardOverview" @click="loadOverview">
            <AppIcon name="refresh" size="sm" />
            Actualizar
          </AppButton>
        </div>
      </div>
    </section>

    <FeedbackMessage v-if="store.loadingDashboardOverview" tone="loading" message="Cargando análisis de producción..." />

    <FeedbackMessage v-else-if="store.dashboardOverviewError" tone="error" title="No se pudo cargar el análisis" :message="store.dashboardOverviewError">
      <AppButton variant="secondary" size="sm" class="mt-3" :loading="store.loadingDashboardOverview" @click="loadOverview">
        <AppIcon name="refresh" size="sm" />
        Reintentar
      </AppButton>
    </FeedbackMessage>

    <div v-else-if="!overview" class="app-card rounded-lg p-5 text-center">
      <p class="font-bold text-[var(--app-text)]">No se pudo preparar el análisis de producción</p>
      <p class="mt-1 text-sm text-[var(--app-text-muted)]">Actualizá el rango para volver a consultar la información.</p>
    </div>

    <template v-else>
      <FeedbackMessage
        v-if="!hasRecords"
        tone="info"
        title="Sin registros en el período"
        message="No hay cargas productivas para las fechas seleccionadas. Los indicadores muestran cero porque no existe actividad registrada en este rango."
      />

      <section class="min-w-0 grid gap-3 xl:grid-cols-[minmax(0,1.35fr)_minmax(22rem,0.65fr)]">
        <div class="app-card min-w-0 rounded-lg p-4">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-wide text-[var(--app-text-soft)]">Producción total</p>
              <div class="mt-2 flex flex-wrap items-end gap-x-3 gap-y-1">
                <span class="text-4xl font-extrabold text-[var(--app-text)] md:text-5xl">
                  {{ formatNumber(totals.produccion_total) }}
                </span>
                <span class="pb-1 text-sm font-bold uppercase tracking-wide text-[var(--app-text-soft)]">prod.</span>
              </div>
              <p class="mt-2 text-sm text-[var(--app-text-muted)]">
                {{ formatNumber(totals.total_registros) }} registros - {{ formatNumber(totals.unidades_activas) }} unidades con actividad
              </p>
            </div>

            <div class="rounded-lg border px-3 py-2" :class="variationTone(primaryVariation)">
              <p class="text-[11px] font-bold uppercase tracking-wide">Periodo anterior</p>
              <p class="mt-1 text-xl font-extrabold">{{ variationLabel(primaryVariation) }}</p>
              <p class="text-xs">{{ previousRangeLabel }}</p>
            </div>
          </div>

          <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <div
              v-for="metric in metricCards"
              :key="metric.label"
              class="app-surface-muted rounded-lg border p-3"
            >
              <div class="flex items-center justify-between gap-3">
                <p class="text-xs font-bold uppercase tracking-wide text-[var(--app-text-soft)]">{{ metric.label }}</p>
                <AppIcon :name="metric.icon" size="sm" class="text-primary" />
              </div>
              <p class="mt-2 text-2xl font-extrabold text-[var(--app-text)]">{{ metric.value }}</p>
              <p class="mt-1 text-xs text-[var(--app-text-muted)]">{{ metric.detail }}</p>
            </div>
          </div>
        </div>

        <aside class="app-card min-w-0 rounded-lg p-4">
          <p class="text-xs font-bold uppercase tracking-wide text-[var(--app-text-soft)]">Comparativa</p>
          <h3 class="mt-1 text-lg font-extrabold text-[var(--app-text)]">Contra periodo anterior</h3>

          <div class="mt-4 divide-y divide-[var(--app-border)]">
            <div v-for="item in overview.variations" :key="item.key" class="py-3">
              <div class="flex items-center justify-between gap-3">
                <span class="text-sm font-bold text-[var(--app-text)]">{{ item.label }}</span>
                <span class="rounded-lg px-2 py-1 text-xs font-extrabold" :class="variationTone(item)">
                  {{ variationLabel(item) }}
                </span>
              </div>
              <div class="mt-1 flex items-center justify-between gap-3 text-xs text-[var(--app-text-soft)]">
                <span>Actual {{ formatNumber(item.current) }}</span>
                <span>Anterior {{ formatNumber(item.previous) }}</span>
              </div>
            </div>
          </div>
        </aside>
      </section>

      <section class="min-w-0 grid gap-3 xl:grid-cols-[minmax(0,1.25fr)_minmax(22rem,0.75fr)]">
        <div class="app-card min-w-0 rounded-lg p-4">
          <div class="mb-3 flex flex-wrap items-end justify-between gap-2">
            <div>
              <p class="text-xs font-bold uppercase tracking-wide text-[var(--app-text-soft)]">Evolución diaria</p>
              <h3 class="mt-1 text-lg font-extrabold text-[var(--app-text)]">Producción del periodo</h3>
            </div>
            <p class="max-w-full text-right text-xs font-semibold text-[var(--app-text-soft)]">{{ overview.evolucion.length }} días con datos</p>
          </div>

          <div v-if="chartPoints.length > 1" class="min-h-64 min-w-0 overflow-hidden">
            <svg
              :viewBox="`0 0 ${chartW} ${chartH}`"
              class="block h-64 w-full max-w-full"
              role="img"
              aria-labelledby="admin-chart-title admin-chart-description"
              preserveAspectRatio="none"
            >
              <title id="admin-chart-title">Producción diaria del período</title>
              <desc id="admin-chart-description">{{ chartAccessibilityDescription }}</desc>
              <line
                v-for="line in chartGrid"
                :key="line"
                :x1="chartPad"
                :x2="chartW - chartPad"
                :y1="line"
                :y2="line"
                stroke="var(--app-border)"
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
                fill="var(--app-surface)"
                stroke="var(--color-primary-dark)"
                stroke-width="2"
              />
            </svg>
            <div class="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold text-[var(--app-text-soft)]">
              <span>{{ firstEvolutionDate }}</span>
              <span>{{ lastEvolutionDate }}</span>
            </div>
          </div>

          <div v-else class="app-surface-muted flex h-64 items-center justify-center rounded-lg border border-dashed text-sm text-[var(--app-text-muted)]">
            Sin evolución suficiente para graficar.
          </div>
        </div>

        <aside class="app-card min-w-0 rounded-lg p-4">
          <p class="text-xs font-bold uppercase tracking-wide text-[var(--app-text-soft)]">Ranking</p>
          <h3 class="mt-1 text-lg font-extrabold text-[var(--app-text)]">Unidades por producción</h3>
          <p v-if="rankingScopeLabel" class="mt-1 text-xs font-semibold text-[var(--app-text-soft)]">{{ rankingScopeLabel }}</p>

          <div v-if="overview.unidad_ranking.length > 0" class="mt-4 space-y-3">
            <div v-for="(item, index) in overview.unidad_ranking" :key="item.id || item.nombre">
              <div class="flex items-center justify-between gap-3">
                <div class="flex min-w-0 items-center gap-2">
                  <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-info-light text-xs font-extrabold text-info-dark">
                    {{ index + 1 }}
                  </span>
                  <div class="min-w-0">
                    <p class="truncate text-sm font-extrabold text-[var(--app-text)]">{{ item.nombre }}</p>
                    <p class="text-xs text-[var(--app-text-soft)]">{{ formatNumber(item.registros) }} registros</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm font-extrabold text-[var(--app-text)]">{{ formatNumber(item.produccion) }}</p>
                  <p class="text-xs text-[var(--app-text-soft)]">{{ formatNumber(item.share_percent) }}%</p>
                </div>
              </div>
              <div class="app-surface-muted mt-2 h-2 overflow-hidden rounded-full">
                <div class="h-full rounded-full bg-primary" :style="{ width: `${Math.min(item.share_percent, 100)}%` }"></div>
              </div>
            </div>
          </div>

          <div v-else class="app-surface-muted mt-3 rounded-lg border border-dashed p-4 text-center text-sm text-[var(--app-text-muted)]">
            Sin unidades con producción en este periodo.
          </div>
        </aside>
      </section>

      <section class="min-w-0 grid gap-3 xl:grid-cols-2">
        <div class="app-card min-w-0 rounded-lg p-4">
          <div class="mb-3">
            <p class="text-xs font-bold uppercase tracking-wide text-[var(--app-text-soft)]">Procesos</p>
            <h3 class="mt-1 text-lg font-extrabold text-[var(--app-text)]">Producción por proceso</h3>
          </div>

          <div v-if="overview.proceso_ranking.length > 0" class="app-table min-w-0 overflow-x-auto rounded-lg">
            <table class="w-full min-w-0 border-collapse text-left text-sm">
              <thead class="app-table-head text-xs uppercase tracking-wide text-[var(--app-text-muted)]">
                <tr>
                  <th class="px-3 py-2.5 font-bold">Proceso</th>
                  <th class="px-3 py-2.5 text-right font-bold">Producción</th>
                  <th class="px-3 py-2.5 text-right font-bold">TN</th>
                  <th class="px-3 py-2.5 text-right font-bold">Reg.</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in overview.proceso_ranking" :key="item.id || item.nombre" class="app-table-row border-t">
                  <td class="break-words px-3 py-2.5 font-bold text-[var(--app-text)]">{{ item.nombre }}</td>
                  <td class="px-3 py-2.5 text-right font-extrabold text-info-dark">{{ formatNumber(item.produccion) }}</td>
                  <td class="px-3 py-2.5 text-right text-[var(--app-text-muted)]">{{ formatNumber(item.tn_despachadas) }}</td>
                  <td class="px-3 py-2.5 text-right text-[var(--app-text-muted)]">{{ formatNumber(item.registros) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="app-surface-muted rounded-lg border border-dashed p-4 text-center text-sm text-[var(--app-text-muted)]">
            Sin procesos con producción en este periodo.
          </div>
        </div>

        <div class="app-card min-w-0 rounded-lg p-4">
          <div class="mb-3">
            <p class="text-xs font-bold uppercase tracking-wide text-[var(--app-text-soft)]">Actividad reciente</p>
            <h3 class="mt-1 text-lg font-extrabold text-[var(--app-text)]">Últimos registros productivos</h3>
          </div>

          <div v-if="overview.recent_records.length > 0" class="space-y-2">
            <article
              v-for="record in overview.recent_records"
              :key="record.id"
              class="app-surface-muted min-w-0 grid gap-3 rounded-lg border px-3 py-2.5 md:grid-cols-[minmax(0,1fr)_auto] md:items-center"
            >
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="truncate text-sm font-extrabold text-[var(--app-text)]">{{ record.operacion || 'Sin operación' }}</p>
                  <span class="rounded-md border px-2 py-0.5 text-xs font-bold app-state-inactive">
                    {{ formatDate(record.fecha) }}
                  </span>
                </div>
                <p class="mt-1 truncate text-xs text-[var(--app-text-muted)]">
                  {{ record.unidad || 'Sin unidad' }} - {{ record.equipo || 'Sin equipo' }} - {{ record.operador || 'Sin operador' }}
                </p>
              </div>
              <div class="text-sm md:text-right">
                <p class="font-extrabold text-info-dark">{{ formatNumber(record.produccion) }}</p>
                <p class="text-xs text-[var(--app-text-soft)]">{{ formatNumber(record.combustible) }} L</p>
              </div>
            </article>
          </div>

          <div v-else class="app-surface-muted rounded-lg border border-dashed p-4 text-center text-sm text-[var(--app-text-muted)]">
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
import AppButton from '@/components/ui/AppButton.vue'
import FeedbackMessage from '@/components/ui/FeedbackMessage.vue'
import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()

const rangePresets = [
  { key: 'today', label: 'Hoy' },
  { key: '7d', label: 'Últimos 7 días' },
  { key: '30d', label: 'Últimos 30 días' },
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
const hasRecords = computed(() => Number(totals.value.total_registros || 0) > 0)

const primaryVariation = computed(() => {
  return overview.value?.variations?.find((item) => item.key === 'produccion_total') || null
})

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
const chartAccessibilityDescription = computed(() => {
  const rows = overview.value?.evolucion || []
  return `Gráfico de línea con ${rows.length} días con datos, desde ${firstEvolutionDate.value} hasta ${lastEvolutionDate.value}.`
})
const rankingScopeLabel = computed(() => {
  const displayed = overview.value?.unidad_ranking?.length || 0
  const active = Number(totals.value.unidades_activas || 0)
  if (!displayed || !active) return ''
  if (active > displayed) return `Mostrando ${formatNumber(displayed)} de ${formatNumber(active)} unidades activas`
  return `${formatNumber(displayed)} unidades activas`
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
  if (!store.dashboardOverviewError) lastUpdated.value = new Date()
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
  if (!item || item.variation_percent == null) return 'app-state-inactive'
  if (Number(item.variation_percent) >= 0) return 'border-success-light bg-success-light/30 text-success-dark'
  return 'border-error-light bg-error-light/40 text-error-dark'
}

onMounted(() => {
  applyPreset('30d')
})
</script>
