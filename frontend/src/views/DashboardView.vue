<template>
  <div class="min-h-screen bg-neutral-100 pb-24 md:pb-8">
    <div class="border-b border-neutral-200 bg-white">
      <div class="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div class="mb-2 flex flex-wrap items-center gap-2">
            <span class="rounded-full border px-3 py-1 text-xs font-bold app-chip-info">
              {{ selectedUnitName || 'Sin unidad' }}
            </span>
            <span class="rounded-full bg-neutral-100 px-3 py-1 text-xs font-bold text-neutral-600">
              {{ dateRangeLabel }}
            </span>
            <span v-if="store.isLoading" class="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-3 py-1 text-xs font-bold text-neutral-500">
              <AppIcon name="loading" size="xs" class="animate-spin" />
              Actualizando
            </span>
          </div>
          <h1 class="text-xl font-extrabold text-neutral-950 md:text-2xl">Dashboard de Produccion</h1>
          <p class="mt-0.5 text-sm text-neutral-500">{{ authStore.userName }} · Lectura operativa y comparativa</p>
        </div>

        <div class="flex flex-wrap gap-2">
          <button type="button" class="inline-flex items-center gap-2 rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm font-bold text-neutral-700 transition-colors hover:border-secondary/40 hover:text-info-dark" @click="refreshDashboard">
            <AppIcon name="refresh" size="sm" />
            Actualizar
          </button>
          <button type="button" class="inline-flex items-center gap-2 rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm font-bold text-neutral-700 transition-colors hover:border-secondary/40 hover:text-info-dark" @click="exportCsv">
            <AppIcon name="download" size="sm" />
            Exportar CSV
          </button>
          <button type="button" class="inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-extrabold text-on-primary transition-colors hover:bg-primary-dark" @click="router.push({ name: 'mis-registros' })">
            <AppIcon name="records" size="sm" />
            Ver detalle
          </button>
        </div>
      </div>
    </div>

    <div class="sticky top-0 z-30 border-b border-neutral-200 bg-white/95 shadow-sm backdrop-blur-sm">
      <div class="mx-auto max-w-7xl px-4 py-3">
        <button
          type="button"
          @click="showFilters = !showFilters"
          class="flex w-full items-center justify-between text-sm font-extrabold text-neutral-700 md:hidden"
        >
          <span class="flex items-center gap-2">
            <AppIcon name="filter" size="sm" />
            Filtros
            <span v-if="store.filtrosActivos" class="flex h-5 w-5 items-center justify-center rounded-full bg-secondary text-xs text-white">{{ store.filtrosActivos }}</span>
          </span>
          <AppIcon name="chevronDown" size="sm" :class="['transition-transform', showFilters ? 'rotate-180' : '']" />
        </button>

        <div :class="['gap-3', showFilters ? 'mt-3 grid' : 'hidden md:grid']">
          <div class="flex flex-wrap items-center gap-2">
            <button
              v-for="preset in datePresets"
              :key="preset.key"
              type="button"
              :class="datePresetClass(preset.key)"
              @click="applyDatePreset(preset.key)"
            >
              {{ preset.label }}
            </button>
            <span class="ml-auto hidden text-xs font-bold uppercase tracking-wide text-neutral-400 md:inline">Filtros principales</span>
          </div>

          <div class="app-card grid gap-3 rounded-lg p-3 md:grid-cols-[1.25fr_1fr_1fr_.75fr_.75fr_auto] md:items-end">
            <AutocompleteField
              v-model="unidadNegocioFilter"
              label="Unidad de Negocio"
              :items="unidadOptions"
              labelKey="nombre"
              valueKey="idUnidadNegocio"
              placeholder="Seleccionar unidad"
              :disabled="unidadOptions.length === 0"
            />

            <AutocompleteField
              v-model="tipoProcesoFilter"
              label="Tipo de Proceso"
              :items="store.tiposProceso"
              labelKey="nombre"
              valueKey="value"
              placeholder="Todos los procesos"
            />

            <div>
              <label class="mb-1 block text-xs font-medium text-neutral-500">Maquina / Equipo</label>
              <AutocompleteField
                v-model="movilFilter"
                :items="movilOptions"
                labelKey="_label"
                valueKey="idMovil"
                placeholder="Todas las maquinas"
              />
            </div>

            <div>
              <label class="mb-1 block text-xs font-medium text-neutral-500">Desde</label>
              <input
                type="date"
                :value="store.filtros.fecha_desde"
                @change="setDateFilter('fecha_desde', $event.target.value || null)"
                class="w-full rounded-lg border border-neutral-300 bg-neutral-50 px-3 py-2 text-sm focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
            </div>

            <div>
              <label class="mb-1 block text-xs font-medium text-neutral-500">Hasta</label>
              <input
                type="date"
                :value="store.filtros.fecha_hasta"
                @change="setDateFilter('fecha_hasta', $event.target.value || null)"
                class="w-full rounded-lg border border-neutral-300 bg-neutral-50 px-3 py-2 text-sm focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
            </div>

            <button
              type="button"
              @click="store.limpiarFiltros()"
              class="rounded-lg border border-neutral-300 px-4 py-2 text-sm font-bold text-neutral-500 transition-colors hover:bg-neutral-50 hover:text-neutral-800"
            >
              Limpiar
            </button>
          </div>

          <div v-if="activeFilterChips.length > 0" class="flex flex-wrap gap-2">
            <span v-for="chip in activeFilterChips" :key="chip" class="rounded-full border px-3 py-1 text-xs font-bold app-chip-info">
              {{ chip }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <main class="mx-auto max-w-7xl space-y-5 px-4 py-5">
      <section v-if="missingUn" class="rounded-lg border border-warning bg-warning-light p-6 text-center">
        <AppIcon name="warning" size="xl" :stroke-width="1.8" class="mx-auto mb-3 text-warning-dark" />
        <p class="mb-1 text-base font-bold text-warning-dark">Sin unidades disponibles</p>
        <p class="text-sm text-neutral-600">No se encontraron unidades de negocio habilitadas para consultar el dashboard.</p>
        <button type="button" @click="handleRelogin" class="mt-4 rounded-lg bg-warning-dark px-6 py-2 text-sm font-semibold text-white transition-colors hover:bg-warning">
          Cerrar sesion
        </button>
      </section>

      <section v-else class="grid gap-4 lg:grid-cols-[1.6fr_.9fr]">
        <div class="app-card app-hover-glow rounded-lg p-5">
          <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <div class="mb-2 flex items-center gap-2 text-sm font-bold text-primary-dark">
                <AppIcon :name="getIconName(store.kpiPrincipal?.icono)" size="sm" />
                {{ store.kpiPrincipal?.nombre || 'Metrica principal' }}
              </div>
              <div v-if="store.loading.kpis" class="h-12 w-56 animate-pulse rounded bg-white/15"></div>
              <div v-else class="flex items-baseline gap-3">
                <span class="text-4xl font-extrabold tracking-normal text-neutral-950 md:text-5xl">{{ animatedHeroValue }}</span>
                <span class="text-lg font-bold text-neutral-500">{{ store.kpiPrincipal?.unidad || '' }}</span>
              </div>
            </div>
            <div class="max-w-md rounded-lg border border-neutral-200 bg-neutral-50 p-4">
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Resumen ejecutivo</p>
              <p class="mt-2 text-sm font-semibold leading-6 text-neutral-800">{{ executiveSummary }}</p>
            </div>
          </div>
          <div v-if="store.kpiPrincipal?.variacion_porcentual != null" class="mt-4">
            <span :class="trendBadgeClass(store.kpiPrincipal)">
              <AppIcon :name="Number(store.kpiPrincipal.variacion_porcentual) >= 0 ? 'arrowUp' : 'arrowDown'" size="xs" :stroke-width="3" />
              {{ Math.abs(store.kpiPrincipal.variacion_porcentual) }}% vs periodo anterior
            </span>
          </div>
        </div>

        <div class="app-card rounded-lg p-5">
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Lectura rapida</p>
          <div class="mt-4 space-y-3 text-sm">
            <div class="flex items-center justify-between gap-3">
              <span class="text-neutral-500">Unidad</span>
              <span class="truncate font-extrabold text-neutral-900">{{ selectedUnitName || 'Sin seleccionar' }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-neutral-500">Periodo</span>
              <span class="font-extrabold text-neutral-900">{{ dateRangeLabel }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-neutral-500">Registros</span>
              <span class="font-extrabold text-neutral-900">{{ formatNumber(periodRecords) }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-neutral-500">Filtros activos</span>
              <span class="font-extrabold text-neutral-900">{{ store.filtrosActivos }}</span>
            </div>
          </div>
        </div>
      </section>

      <section v-if="store.loading.kpis" class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div v-for="i in 5" :key="i" class="rounded-lg border border-neutral-200 bg-white p-4">
          <div class="mb-4 h-8 w-8 animate-pulse rounded-lg bg-neutral-100"></div>
          <div class="mb-2 h-4 w-3/4 animate-pulse rounded bg-neutral-100"></div>
          <div class="h-7 w-1/2 animate-pulse rounded bg-neutral-200"></div>
        </div>
      </section>

      <section v-else-if="store.kpisSecundarios.length > 0" :class="secondaryKpiGridClass">
        <article
          v-for="kpi in store.kpisSecundarios"
          :key="kpi.id"
          class="app-card rounded-lg p-4 transition-colors hover:border-secondary/30"
        >
          <div class="mb-3 flex items-start justify-between gap-3">
            <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-info-light text-info-dark">
              <AppIcon :name="getIconName(kpi.icono)" size="sm" />
            </span>
            <span v-if="kpi.variacion_porcentual != null" :class="trendBadgeClass(kpi)">
              {{ Number(kpi.variacion_porcentual) >= 0 ? '+' : '-' }}{{ Math.abs(kpi.variacion_porcentual) }}%
            </span>
          </div>
          <p class="min-h-8 text-xs font-bold uppercase leading-4 text-neutral-400">{{ kpi.nombre }}</p>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-2xl font-extrabold text-neutral-950">{{ formatNumber(kpi.valor) }}</span>
            <span class="text-xs font-bold text-neutral-400">{{ kpi.unidad }}</span>
          </div>
        </article>
      </section>

      <section v-else-if="!store.loading.kpis">
        <EmptyState
          title="No hay datos para los filtros seleccionados"
          :description="emptyFilterMessage"
          icon="empty"
        >
          <button type="button" class="rounded-lg bg-primary px-4 py-2 text-sm font-extrabold text-on-primary" @click="store.limpiarFiltros()">
            Restablecer filtros
          </button>
        </EmptyState>
      </section>

      <section class="grid grid-cols-1 gap-5 lg:grid-cols-5">
        <div class="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm lg:col-span-3">
          <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Evolucion diaria</p>
              <h2 class="text-lg font-extrabold text-neutral-950">{{ chartTitle }}</h2>
            </div>
            <div class="flex flex-wrap gap-2">
              <button type="button" :class="metricTabClass('produccion')" @click="activeChartMetric = 'produccion'">
                Produccion
              </button>
              <button type="button" :class="metricTabClass('combustible')" @click="activeChartMetric = 'combustible'">
                Combustible
              </button>
            </div>
          </div>

          <div class="mb-4 grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
            <AutocompleteField
              v-model="evolucionTipoProcesoFilter"
              label="Tipo de Proceso"
              :items="store.tiposProceso"
              labelKey="nombre"
              valueKey="value"
              placeholder="Todos los procesos"
              selectedDisplay="input"
            />
            <button type="button" class="rounded-lg border border-neutral-200 px-4 py-2 text-sm font-bold text-neutral-600 hover:border-secondary/40" @click="router.push({ name: 'mis-registros' })">
              Abrir registros
            </button>
          </div>

          <div v-if="activeChartLoading" class="flex h-72 items-center justify-center">
            <div class="h-8 w-8 animate-spin rounded-full border-3 border-primary border-t-transparent"></div>
          </div>

          <div v-else-if="chartPoints.length > 1" class="relative" @mouseleave="tooltip = null">
            <svg :viewBox="`0 0 ${chartW} ${chartH + 30}`" class="w-full" preserveAspectRatio="xMidYMid meet">
              <line v-for="i in 4" :key="'g'+i"
                :x1="chartPad" :y1="chartH - (chartH - chartPad) * (i/4)" :x2="chartW - chartPad" :y2="chartH - (chartH - chartPad) * (i/4)"
                stroke="var(--color-neutral-200)" stroke-width="0.5" stroke-dasharray="4 4"
              />
              <text v-for="i in 4" :key="'yl'+i"
                :x="chartPad - 4" :y="chartH - (chartH - chartPad) * (i/4) + 3"
                text-anchor="end" fill="var(--color-neutral-400)" font-size="9"
              >{{ formatNumber(maxVal * i / 4) }}</text>
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" :stop-color="activeChartMetric === 'combustible' ? 'var(--color-warning)' : 'var(--color-primary)'" stop-opacity="0.24"/>
                  <stop offset="100%" :stop-color="activeChartMetric === 'combustible' ? 'var(--color-warning)' : 'var(--color-primary)'" stop-opacity="0.02"/>
                </linearGradient>
              </defs>
              <path :d="areaPath" fill="url(#areaGrad)" />
              <polyline :points="linePoints" fill="none" :stroke="activeChartMetric === 'combustible' ? 'var(--color-warning-dark)' : 'var(--color-primary)'" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
              <circle
                v-for="(p, i) in chartPoints" :key="'p'+i"
                :cx="p.x" :cy="p.y" r="4"
                fill="white" :stroke="activeChartMetric === 'combustible' ? 'var(--color-warning-dark)' : 'var(--color-primary)'" stroke-width="2"
                class="cursor-pointer"
                @mouseenter="tooltip = { x: p.x, y: p.y, label: activeChartData.labels[i], value: activeChartValues[i] }"
              />
              <text v-for="(p, i) in chartXLabels" :key="'xl'+i"
                :x="p.x" :y="chartH + 20" text-anchor="middle" fill="var(--color-neutral-400)" font-size="8"
              >{{ p.label }}</text>
            </svg>

            <div v-if="tooltip"
              class="absolute pointer-events-none rounded-lg bg-neutral-900 px-3 py-1.5 text-xs text-white shadow-lg"
              :style="{ left: `${(tooltip.x / chartW) * 100}%`, top: `${(tooltip.y / (chartH + 30)) * 100 - 10}%`, transform: 'translate(-50%, -100%)' }"
            >
              <div class="font-bold">{{ formatNumber(tooltip.value) }} {{ activeChartUnit }}</div>
              <div class="text-[10px] text-neutral-400">{{ tooltip.label }}</div>
            </div>
          </div>

          <div v-else class="h-72 flex items-center justify-center">
            <EmptyState
              title="Sin datos de evolucion para el periodo"
              description="Proba ampliar fechas, cambiar la unidad o quitar filtros de proceso/equipo."
              icon="empty"
            />
          </div>
        </div>

        <div class="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm lg:col-span-2">
          <div class="mb-4 flex items-start justify-between gap-3">
            <div>
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Ranking</p>
              <h2 class="text-lg font-extrabold text-neutral-950">Maquinas</h2>
            </div>
            <button type="button" class="rounded-lg border border-neutral-200 px-3 py-2 text-xs font-bold text-neutral-600 hover:border-secondary/40" @click="exportCsv">
              CSV
            </button>
          </div>

          <div class="mb-4 space-y-3">
            <AutocompleteField
              v-model="rankingTipoProcesoFilter"
              label="Tipo de Proceso"
              :items="store.tiposProceso"
              labelKey="nombre"
              valueKey="value"
              placeholder="Todos los procesos"
              selectedDisplay="input"
            />
            <div class="grid grid-cols-2 gap-2">
              <button type="button" :class="rankingMetricClass('produccion')" @click="store.setRankingMetric('produccion')">
                Produccion
              </button>
              <button type="button" :class="rankingMetricClass('combustible')" @click="store.setRankingMetric('combustible')">
                Combustible
              </button>
            </div>
          </div>

          <div v-if="store.loading.ranking" class="space-y-4">
            <div v-for="i in 5" :key="i" class="animate-pulse">
              <div class="mb-2 h-3 w-2/3 rounded bg-neutral-200"></div>
              <div class="h-5 rounded bg-neutral-100"></div>
            </div>
          </div>

          <div v-else-if="store.rankingMaquinas.length > 0" class="space-y-3">
            <div v-for="(item, idx) in store.rankingMaquinas" :key="idx" class="group">
              <div class="mb-1 flex items-center justify-between">
                <div class="flex min-w-0 items-center gap-2">
                  <span :class="[
                    'flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-extrabold',
                    idx === 0 ? 'bg-secondary text-white shadow-sm' : idx === 1 ? 'bg-info-light text-info-dark' : idx === 2 ? 'bg-warning-light text-warning-dark' : 'bg-neutral-100 text-neutral-500'
                  ]">{{ idx + 1 }}</span>
                  <div class="min-w-0">
                    <p class="truncate text-sm font-bold text-neutral-800">{{ item.patente }}</p>
                    <p class="truncate text-[11px] text-neutral-400">{{ item.detalle }}</p>
                  </div>
                </div>
                <div class="ml-2 shrink-0 text-right">
                  <span class="text-sm font-extrabold text-neutral-900">{{ formatNumber(item.valor) }}</span>
                  <span class="block text-[10px] text-neutral-400">{{ item.registros }} reg.</span>
                </div>
              </div>
              <div class="h-1.5 overflow-hidden rounded-full bg-neutral-100">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="store.filtros.ranking_metric === 'combustible' ? 'bg-warning-dark' : idx === 0 ? 'bg-secondary' : 'bg-info-light'"
                  :style="{ width: `${rankingMaxVal > 0 ? (item.valor / rankingMaxVal * 100) : 0}%` }"
                ></div>
              </div>
            </div>
          </div>

          <div v-else class="h-56 flex items-center justify-center">
            <EmptyState
              title="Sin datos de ranking"
              description="No hay maquinas con actividad para los filtros actuales."
              icon="empty"
            />
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import AutocompleteField from '@/components/AutocompleteField.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

const authStore = useAuthStore()
const store = useDashboardStore()
const router = useRouter()

const showFilters = ref(false)
const tooltip = ref(null)
const activeChartMetric = ref('produccion')

const datePresets = [
  { key: 'today', label: 'Hoy' },
  { key: 'yesterday', label: 'Ayer' },
  { key: '7days', label: '7 dias' },
  { key: 'lastWeek', label: 'Semana pasada' },
  { key: 'month', label: 'Mes actual' },
]

const unidadNegocioFilter = computed({
  get: () => store.filtros.un_id || '',
  set: (value) => store.setUnidadNegocio(value),
})

const userUnidadIds = computed(() => {
  const ids = Array.isArray(authStore.user?.unidad_ids) ? authStore.user.unidad_ids : []
  const main = authStore.user?.unidad_negocio
  return new Set([...ids, main].map((value) => Number(value || 0)).filter(Boolean))
})

const unidadOptions = computed(() => {
  if (authStore.isAdmin) return store.unidadesNegocio
  return store.unidadesNegocio.filter((unidad) => userUnidadIds.value.has(Number(unidad.idUnidadNegocio)))
})

const selectedUnitName = computed(() => {
  return unidadOptions.value.find((item) => String(item.idUnidadNegocio) === String(store.filtros.un_id || ''))?.nombre || ''
})

const tipoProcesoFilter = computed({
  get: () => store.filtros.tipo_proceso_key || '',
  set: (value) => store.setFiltro('tipo_proceso_key', value || null),
})

const evolucionTipoProcesoFilter = computed({
  get: () => store.filtros.evolucion_tipo_proceso_key || '',
  set: (value) => store.setEvolucionTipoProceso(value || null),
})

const rankingTipoProcesoFilter = computed({
  get: () => store.filtros.ranking_tipo_proceso_key || '',
  set: (value) => store.setRankingTipoProceso(value || null),
})

const movilFilter = computed({
  get: () => store.filtros.movil_id || '',
  set: (value) => store.setFiltro('movil_id', value ? Number(value) : null),
})

const movilOptions = computed(() => {
  return store.movilesDisponibles.map((movil) => ({
    ...movil,
    _label: [movil.patente, movil.detalle].filter(Boolean).join(' - '),
  }))
})

const activeFilterChips = computed(() => {
  const chips = []
  const proceso = store.tiposProceso.find((item) => String(item.value) === String(store.filtros.tipo_proceso_key || ''))
  const movil = movilOptions.value.find((item) => String(item.idMovil) === String(store.filtros.movil_id || ''))

  if (selectedUnitName.value) chips.push(selectedUnitName.value)
  if (proceso?.nombre) chips.push(proceso.nombre)
  if (movil?._label) chips.push(movil._label)
  if (store.filtros.fecha_desde || store.filtros.fecha_hasta) chips.push(dateRangeLabel.value)
  return chips
})

const dateRangeLabel = computed(() => {
  const from = formatDateShort(store.filtros.fecha_desde)
  const to = formatDateShort(store.filtros.fecha_hasta)
  if (from && to && from === to) return from
  return `${from || 'Inicio'} - ${to || 'Hoy'}`
})

const emptyFilterMessage = computed(() => {
  if (activeFilterChips.value.length === 0) return 'Proba modificando el rango de fechas o los filtros.'
  return `Sin resultados para: ${activeFilterChips.value.join(', ')}. Proba ampliando fechas o quitando algun filtro.`
})

const secondaryKpiGridClass = computed(() => {
  const count = store.kpisSecundarios.length
  const desktopCols = count >= 5 ? 'lg:grid-cols-5' : count === 4 ? 'lg:grid-cols-4' : 'lg:grid-cols-3'
  return ['grid grid-cols-1 gap-3 sm:grid-cols-2', desktopCols]
})

const periodRecords = computed(() => {
  return store.kpis.find((kpi) => String(kpi.nombre || '').toLowerCase().includes('registro'))?.valor || 0
})

const executiveSummary = computed(() => {
  if (store.loading.kpis) return 'Cargando metricas para el periodo seleccionado.'
  if (!store.kpiPrincipal) return 'Sin datos suficientes para generar lectura del periodo.'
  const primary = `${formatNumber(store.kpiPrincipal.valor)} ${store.kpiPrincipal.unidad || ''}`.trim()
  const efficiency = store.kpis.find((kpi) => String(kpi.nombre || '').toLowerCase().includes('eficiencia'))
  const fuel = store.kpis.find((kpi) => String(kpi.nombre || '').toLowerCase().includes('combustible'))
  const parts = [`${store.kpiPrincipal.nombre}: ${primary}`]
  if (efficiency) parts.push(`eficiencia ${formatNumber(efficiency.valor)}${efficiency.unidad || ''}`)
  if (fuel) parts.push(`combustible ${formatNumber(fuel.valor)} ${fuel.unidad || ''}`.trim())
  return `${parts.join(' · ')}.`
})

function handleRelogin() {
  authStore.logout()
  router.push({ name: 'login' })
}

async function refreshDashboard() {
  await store.fetchAll()
}

async function setDateFilter(field, value) {
  await store.setFiltro(field, value)
}

async function applyDatePreset(key) {
  const today = startOfDay(new Date())
  let from = today
  let to = today

  if (key === 'yesterday') {
    from = addDays(today, -1)
    to = addDays(today, -1)
  } else if (key === '7days') {
    from = addDays(today, -6)
  } else if (key === 'lastWeek') {
    const day = today.getDay() || 7
    to = addDays(today, -day)
    from = addDays(to, -6)
  } else if (key === 'month') {
    from = new Date(today.getFullYear(), today.getMonth(), 1)
    to = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  }

  store.filtros.fecha_desde = toISODate(from)
  store.filtros.fecha_hasta = toISODate(to)
  await store.fetchAll()
  store.persistFiltros()
}

function datePresetClass(key) {
  return [
    'rounded-lg border px-3 py-2 text-xs font-bold transition-colors',
    isDatePresetActive(key)
      ? 'border-secondary bg-secondary text-white'
      : 'border-neutral-200 bg-white text-neutral-600 hover:border-secondary/40 hover:text-info-dark',
  ]
}

function isDatePresetActive(key) {
  const current = `${store.filtros.fecha_desde || ''}|${store.filtros.fecha_hasta || ''}`
  const today = startOfDay(new Date())
  const ranges = {
    today: [today, today],
    yesterday: [addDays(today, -1), addDays(today, -1)],
    '7days': [addDays(today, -6), today],
    lastWeek: [addDays(addDays(today, -(today.getDay() || 7)), -6), addDays(today, -(today.getDay() || 7))],
    month: [new Date(today.getFullYear(), today.getMonth(), 1), new Date(today.getFullYear(), today.getMonth() + 1, 0)],
  }
  const range = ranges[key]
  return range ? current === `${toISODate(range[0])}|${toISODate(range[1])}` : false
}

const animatedHeroValue = ref('0')

function animateValue(start, end, duration = 600) {
  const startTime = performance.now()
  const step = (now) => {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    const current = start + (end - start) * eased
    animatedHeroValue.value = formatNumber(current)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

watch(() => store.kpiPrincipal?.valor, (newVal, oldVal) => {
  if (newVal != null) animateValue(oldVal || 0, newVal)
})

const iconMap = {
  truck: 'truck',
  box: 'empty',
  leaf: 'leaf',
  layers: 'process',
  route: 'location',
  'map-pin': 'location',
  map: 'field',
  'grid-3x3': 'dashboard',
  clock: 'timer',
  fuel: 'fuel',
  'alert-circle': 'warning',
  timer: 'timer',
  percent: 'dashboard',
  'clipboard-list': 'records',
}

function rankingMetricClass(metric) {
  return [
    'rounded-lg border px-3 py-2 text-xs font-bold transition-colors',
    store.filtros.ranking_metric === metric
      ? 'border-secondary bg-secondary text-white'
      : 'border-neutral-200 bg-neutral-50 text-neutral-600 hover:border-secondary/40',
  ]
}

function metricTabClass(metric) {
  return [
    'rounded-lg border px-3 py-2 text-xs font-bold transition-colors',
    activeChartMetric.value === metric
      ? 'border-secondary bg-secondary text-white'
      : 'border-neutral-200 bg-white text-neutral-600 hover:border-secondary/40',
  ]
}

function trendBadgeClass(kpi) {
  const variation = Number(kpi?.variacion_porcentual || 0)
  const name = String(kpi?.nombre || '').toLowerCase()
  const isConsumption = name.includes('combustible')
  if (variation === 0) return 'inline-flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-bold app-state-inactive'
  if (isConsumption && variation > 0) return 'inline-flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-bold app-state-idle'
  if (variation > 0) return 'inline-flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-bold app-state-active'
  if (isConsumption) return 'inline-flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-bold app-state-active'
  return 'inline-flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-bold app-state-incident'
}

function getIconName(name) {
  return iconMap[name] || 'empty'
}

function formatNumber(val) {
  if (val == null) return '0'
  const n = Number(val)
  if (Number.isNaN(n)) return '0'
  if (Number.isInteger(n)) return n.toLocaleString('es-AR')
  return n.toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 2 })
}

function formatDateShort(value) {
  if (!value) return ''
  const [year, month, day] = String(value).split('-')
  if (!year || !month || !day) return value
  return `${day}/${month}/${year}`
}

function toISODate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

function addDays(date, days) {
  const copy = new Date(date)
  copy.setDate(copy.getDate() + days)
  return copy
}

function exportCsv() {
  const rows = [
    ['Dashboard de Produccion'],
    ['Unidad', selectedUnitName.value],
    ['Periodo', dateRangeLabel.value],
    [],
    ['KPI', 'Valor', 'Unidad', 'Variacion %'],
    ...store.kpis.map((kpi) => [kpi.nombre, kpi.valor, kpi.unidad || '', kpi.variacion_porcentual ?? '']),
    [],
    ['Ranking', 'Detalle', 'Valor', 'Registros'],
    ...store.rankingMaquinas.map((item) => [item.patente, item.detalle, item.valor, item.registros]),
  ]
  const csv = rows.map((row) => row.map(csvValue).join(';')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `dashboard-produccion-${store.filtros.fecha_desde || 'inicio'}-${store.filtros.fecha_hasta || 'hoy'}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

function csvValue(value) {
  const text = String(value ?? '')
  return `"${text.replaceAll('"', '""')}"`
}

const chartW = 600
const chartH = 220
const chartPad = 40

const activeChartData = computed(() => (
  activeChartMetric.value === 'combustible' ? store.evolucionCombustible : store.evolucion
))

const activeChartLoading = computed(() => (
  activeChartMetric.value === 'combustible' ? store.loading.evolucionCombustible : store.loading.evolucion
))

const activeChartValues = computed(() => activeChartData.value.datasets?.[0]?.valores || [])
const activeChartUnit = computed(() => (activeChartMetric.value === 'combustible' ? 'L' : (activeChartData.value.datasets?.[0]?.unidad || '')))
const chartTitle = computed(() => activeChartMetric.value === 'combustible' ? 'Combustible consumido' : (activeChartData.value.datasets?.[0]?.nombre || 'Produccion'))

const maxVal = computed(() => Math.max(...activeChartValues.value, 1))

const chartPoints = computed(() => {
  const vals = activeChartValues.value
  if (vals.length < 2) return []
  const usableW = chartW - chartPad * 2
  const usableH = chartH - chartPad
  return vals.map((v, i) => ({
    x: chartPad + (i / (vals.length - 1)) * usableW,
    y: chartH - (v / maxVal.value) * usableH,
  }))
})

const linePoints = computed(() => chartPoints.value.map((p) => `${p.x},${p.y}`).join(' '))

const areaPath = computed(() => {
  const pts = chartPoints.value
  if (pts.length < 2) return ''
  let d = `M ${pts[0].x},${chartH}`
  pts.forEach((p) => (d += ` L ${p.x},${p.y}`))
  d += ` L ${pts[pts.length - 1].x},${chartH} Z`
  return d
})

const chartXLabels = computed(() => {
  const labels = activeChartData.value.labels || []
  const pts = chartPoints.value
  if (pts.length === 0) return []
  const step = Math.max(1, Math.ceil(labels.length / 8))
  return labels.reduce((acc, label, i) => {
    if (i % step === 0 && pts[i]) {
      const short = label.length > 5 ? label.slice(5) : label
      acc.push({ x: pts[i].x, label: short })
    }
    return acc
  }, [])
})

const rankingMaxVal = computed(() => {
  if (store.rankingMaquinas.length === 0) return 1
  return Math.max(...store.rankingMaquinas.map((r) => r.valor), 1)
})

const missingUn = ref(false)

onMounted(async () => {
  await store.loadUnidadesNegocio()

  const savedFilters = store.loadPersistedFiltros()
  const availableUnits = unidadOptions.value.map((unidad) => Number(unidad.idUnidadNegocio))
  const candidates = [
    savedFilters.un_id,
    authStore.user?.unidad_negocio,
    ...(Array.isArray(authStore.user?.unidad_ids) ? authStore.user.unidad_ids : []),
    unidadOptions.value[0]?.idUnidadNegocio,
  ].map((value) => Number(value || 0))
  const unId = candidates.find((value) => value > 0 && availableUnits.includes(value))

  if (!unId) {
    missingUn.value = true
    return
  }

  store.initFiltros(unId)
  await store.loadTiposProceso(unId)
  await store.loadMovilesDisponibles(unId)
  await store.fetchAll()

  await nextTick()
  if (store.kpiPrincipal?.valor) animateValue(0, store.kpiPrincipal.valor)
})
</script>
