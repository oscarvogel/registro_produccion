<template>
  <div class="min-h-screen bg-neutral-100 px-3 py-3 pb-20 md:px-4 md:py-4 md:pb-6">
    <div class="mx-auto max-w-6xl space-y-3">
      <PageHeader
        title="Mis Registros"
        :description="`${authStore.userName} · historial personal y totales del periodo`"
      >
        <template #actions>
          <AppButton variant="secondary" @click="$router.back()">
            <AppIcon name="back" size="sm" />
            Volver
          </AppButton>
          <AppButton @click="$router.push({ name: 'produccion' })">
            <AppIcon name="production" size="sm" />
            Cargar produccion
          </AppButton>
        </template>
      </PageHeader>

      <FilterBar title="Periodo" eyebrow="Filtros rapidos">
        <template #summary>
          <span class="rounded-full border px-3 py-1 text-xs font-bold app-chip-info">
            {{ store.registros.length }} registro{{ store.registros.length !== 1 ? 's' : '' }}
          </span>
        </template>

        <div class="flex flex-wrap gap-2 md:w-full">
          <button
            v-for="preset in datePresets"
            :key="preset.key"
            type="button"
            :class="quickFilterClass(preset.key)"
            @click="applyPreset(preset.key)"
          >
            {{ preset.label }}
          </button>
        </div>

        <div class="min-w-36 flex-1">
          <label class="mb-1 block text-xs font-medium text-neutral-500">Desde</label>
          <input
            type="date"
            :value="store.filtros.fecha_desde"
            @change="handleManualDate('fecha_desde', $event.target.value || null)"
            class="w-full rounded-xl border border-neutral-300 bg-neutral-50 px-3 py-2 text-sm text-neutral-900 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30"
          />
        </div>

        <div class="min-w-36 flex-1">
          <label class="mb-1 block text-xs font-medium text-neutral-500">Hasta</label>
          <input
            type="date"
            :value="store.filtros.fecha_hasta"
            @change="handleManualDate('fecha_hasta', $event.target.value || null)"
            class="w-full rounded-xl border border-neutral-300 bg-neutral-50 px-3 py-2 text-sm text-neutral-900 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30"
          />
        </div>
      </FilterBar>

      <div v-if="store.loading" class="flex justify-center py-16">
        <div class="h-8 w-8 animate-spin rounded-full border-3 border-primary border-t-transparent"></div>
      </div>

      <template v-else>
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Registros" :value="store.totales.total" icon="records" tone="info" />
          <MetricCard label="Horas trabajadas" :value="fmt(store.totales.total_horas)" unit="hs" icon="timer" />
          <MetricCard label="Combustible" :value="fmt(store.totales.total_combustible)" unit="lts" icon="fuel" tone="warning" />
          <MetricCard
            v-if="store.totales.combustible_por_hora != null"
            label="Combustible / hora"
            :value="fmt(store.totales.combustible_por_hora)"
            unit="lts/hs"
            icon="fuel"
            tone="warning"
          />

          <MetricCard
            v-for="metric in productionMetrics"
            :key="metric.label"
            :label="metric.label"
            :value="metric.value"
            :unit="metric.unit"
            :description="metric.detail"
            icon="production"
            tone="info"
          />
        </div>

        <section v-if="store.registros.length > 0" class="space-y-2">
          <h2 class="px-1 text-xs font-extrabold uppercase tracking-wide text-neutral-500">Detalle de registros</h2>

          <article
            v-for="record in store.registros"
            :key="record.id"
            v-motion-panel
            class="rounded-xl border border-neutral-200 bg-white p-3.5 shadow-sm"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <span class="inline-flex max-w-full rounded-lg bg-info-light px-2 py-0.5 text-xs font-bold uppercase tracking-wide text-info-dark">
                  <span class="truncate">{{ record.operacion || 'Produccion' }}</span>
                </span>
                <p class="mt-1 text-xs font-semibold text-neutral-400">{{ formatFecha(record.fecha) }}</p>
              </div>
              <p class="max-w-[11rem] truncate text-right text-xs font-semibold text-neutral-500">
                {{ record.equipo || 'Sin equipo' }}
              </p>
            </div>

            <div class="mt-2.5 flex flex-wrap gap-2">
              <span
                v-for="metric in recordMetrics(record)"
                :key="metric.label"
                :class="[
                  'rounded-lg px-2.5 py-1 text-xs font-extrabold',
                  metric.tone === 'warning' ? 'bg-warning-light text-warning-dark' : 'bg-neutral-100 text-neutral-700',
                ]"
              >
                {{ metric.value }} <span class="font-semibold opacity-70">{{ metric.unit }}</span>
              </span>
            </div>
          </article>
        </section>

        <EmptyState v-else title="No hay registros para este periodo" description="Proba con otro rango de fechas o carga una nueva produccion.">
          <AppButton @click="$router.push({ name: 'produccion' })">
            <AppIcon name="production" size="sm" />
            Cargar produccion
          </AppButton>
        </EmptyState>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMisRegistrosStore } from '@/stores/misRegistros'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import FilterBar from '@/components/ui/FilterBar.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import PageHeader from '@/components/ui/PageHeader.vue'

const authStore = useAuthStore()
const store = useMisRegistrosStore()
const activePreset = ref('month')

const datePresets = [
  { key: 'today', label: 'Hoy' },
  { key: 'week', label: 'Esta semana' },
  { key: 'month', label: 'Este mes' },
]

const productionMetrics = computed(() => {
  const totals = store.totales
  return [
    { label: 'Toneladas despachadas', value: fmt(totals.total_tn), raw: totals.total_tn, unit: 'TN', detail: totals.tn_por_hora != null ? `${fmt(totals.tn_por_hora)} TN/hs` : '' },
    { label: 'Metros cubicos', value: fmt(totals.total_m3), raw: totals.total_m3, unit: 'm3', detail: totals.m3_por_hora != null ? `${fmt(totals.m3_por_hora)} m3/hs` : '' },
    { label: 'Hectareas', value: fmt(totals.total_has), raw: totals.total_has, unit: 'HAS', detail: totals.has_por_hora != null ? `${fmt(totals.has_por_hora)} HAS/hs` : '' },
    { label: 'Carros', value: fmt(totals.total_carros), raw: totals.total_carros, unit: 'uds', detail: totals.carros_por_hora != null ? `${fmt(totals.carros_por_hora)} carros/hs` : '' },
    { label: 'Plantas', value: fmt(totals.total_plantas), raw: totals.total_plantas, unit: 'uds', detail: totals.plantas_por_hora != null ? `${fmt(totals.plantas_por_hora)} plantas/hs` : '' },
    { label: 'KM Carreteo', value: fmt(totals.total_km_carreteo), raw: totals.total_km_carreteo, unit: 'km', detail: totals.km_carreteo_por_hora != null ? `${fmt(totals.km_carreteo_por_hora)} km/hs` : '' },
    { label: 'KM Perfilado', value: fmt(totals.total_km_perfilado), raw: totals.total_km_perfilado, unit: 'km', detail: totals.km_perfilado_por_hora != null ? `${fmt(totals.km_perfilado_por_hora)} km/hs` : '' },
  ].filter((metric) => Number(metric.raw) > 0)
})

function fmt(val) {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function formatFecha(fecha) {
  if (!fecha) return '---'
  const [y, m, d] = String(fecha).split('-')
  if (!y || !m || !d) return fecha
  return `${d}/${m}/${y}`
}

function toIso(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function applyPreset(preset) {
  activePreset.value = preset
  const end = new Date()
  const start = new Date()

  if (preset === 'today') {
    store.setFiltro('fecha_desde', toIso(start))
    store.setFiltro('fecha_hasta', toIso(end))
    return
  }

  if (preset === 'week') {
    const day = start.getDay() || 7
    start.setDate(start.getDate() - day + 1)
    store.setFiltro('fecha_desde', toIso(start))
    store.setFiltro('fecha_hasta', toIso(end))
    return
  }

  store.limpiarFiltros()
}

function handleManualDate(key, value) {
  activePreset.value = 'custom'
  store.setFiltro(key, value)
}

function quickFilterClass(key) {
  return [
    'rounded-full border px-3 py-1.5 text-xs font-bold transition-colors',
    activePreset.value === key
      ? 'border-secondary bg-secondary text-white'
      : 'border-neutral-200 bg-neutral-50 text-neutral-600 hover:border-secondary/40 hover:text-info-dark',
  ]
}

function recordMetrics(record) {
  return [
    { label: 'tn', value: fmt(record.tn_despachadas), raw: record.tn_despachadas, unit: 'TN' },
    { label: 'm3', value: fmt(record.m3), raw: record.m3, unit: 'm3' },
    { label: 'has', value: fmt(record.has), raw: record.has, unit: 'HAS' },
    { label: 'carros', value: fmt(record.carros), raw: record.carros, unit: 'carros' },
    { label: 'plantas', value: fmt(record.plantas), raw: record.plantas, unit: 'plantas' },
    { label: 'km_carreteo', value: fmt(record.km_carreteo), raw: record.km_carreteo, unit: 'km carr.' },
    { label: 'km_perfilado', value: fmt(record.km_perfilado), raw: record.km_perfilado, unit: 'km perf.' },
    { label: 'combustible', value: fmt(record.combustible), raw: record.combustible, unit: 'lts', tone: 'warning' },
  ].filter((metric) => Number(metric.raw) > 0)
}

onMounted(() => {
  store.initFiltros()
  store.fetchMisRegistros()
})
</script>
