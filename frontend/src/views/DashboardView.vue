<template>
  <div class="min-h-screen bg-neutral-100 pb-24 md:pb-8">
    <!-- Header -->
    <div class="bg-white border-b border-neutral-200 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <h1 class="text-xl md:text-2xl font-extrabold text-primary-dark">Dashboard de Producción</h1>
        <p class="text-sm text-neutral-500 mt-0.5">{{ authStore.userName }} · Resumen operativo</p>
      </div>
    </div>

    <!-- Filtros -->
    <div class="sticky top-0 z-30 bg-white border-b border-neutral-200 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-3">
        <!-- Mobile: toggle -->
        <button
          @click="showFilters = !showFilters"
          class="md:hidden flex items-center justify-between w-full text-sm font-medium text-neutral-700"
        >
          <span class="flex items-center gap-2">
            <AppIcon name="filter" size="sm" />
            Filtros
            <span v-if="store.filtrosActivos" class="bg-primary text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">{{ store.filtrosActivos }}</span>
          </span>
          <AppIcon name="chevronDown" size="sm" :class="['transition-transform', showFilters ? 'rotate-180' : '']" />
        </button>

        <!-- Filter row -->
        <div :class="['md:flex md:items-end md:gap-4 flex-wrap', showFilters ? 'mt-3 flex flex-col gap-3' : 'hidden md:flex']">
          <!-- Tipo proceso -->
          <div class="flex-1 min-w-45">
            <AutocompleteField
              v-model="tipoProcesoFilter"
              label="Tipo de Proceso"
              :items="store.tiposProceso"
              labelKey="nombre"
              valueKey="id"
              placeholder="Todos los procesos"
            />
            <button
              v-if="tipoProcesoFilter"
              @click="tipoProcesoFilter = ''"
              class="mt-1 text-xs font-semibold text-neutral-400 underline underline-offset-2 hover:text-neutral-600"
              type="button"
            >
              Limpiar proceso
            </button>
          </div>

          <!-- Máquina -->
          <div class="flex-1 min-w-45">
            <label class="block text-xs font-medium text-neutral-500 mb-1">Máquina / Equipo</label>
            <AutocompleteField
              v-model="movilFilter"
              :items="movilOptions"
              labelKey="_label"
              valueKey="idMovil"
              placeholder="Todas las maquinas"
            />
            <button
              v-if="movilFilter"
              @click="movilFilter = ''"
              class="mt-1 text-xs font-semibold text-neutral-400 underline underline-offset-2 hover:text-neutral-600"
              type="button"
            >
              Limpiar equipo
            </button>
          </div>

          <!-- Fecha desde -->
          <div class="flex-1 min-w-37.5">
            <label class="block text-xs font-medium text-neutral-500 mb-1">Desde</label>
            <input
              type="date"
              :value="store.filtros.fecha_desde"
              @change="store.setFiltro('fecha_desde', $event.target.value || null)"
              class="w-full px-3 py-2 text-sm bg-neutral-50 border border-neutral-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/40"
            />
          </div>

          <!-- Fecha hasta -->
          <div class="flex-1 min-w-37.5">
            <label class="block text-xs font-medium text-neutral-500 mb-1">Hasta</label>
            <input
              type="date"
              :value="store.filtros.fecha_hasta"
              @change="store.setFiltro('fecha_hasta', $event.target.value || null)"
              class="w-full px-3 py-2 text-sm bg-neutral-50 border border-neutral-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/40"
            />
          </div>

          <!-- Limpiar -->
          <button
            @click="store.limpiarFiltros()"
            class="px-4 py-2 text-sm font-medium text-neutral-500 hover:text-neutral-700 border border-neutral-300 rounded-xl hover:bg-neutral-50 transition-colors whitespace-nowrap"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 py-6 space-y-6">

      <!-- Missing UN warning -->
      <div v-if="missingUn" class="bg-warning-light border border-warning rounded-2xl p-6 text-center">
        <AppIcon name="warning" size="xl" :stroke-width="1.8" class="mx-auto mb-3 text-warning-dark" />
        <p class="text-warning-dark font-bold text-base mb-1">Sesión desactualizada</p>
        <p class="text-neutral-600 text-sm">Tu perfil no tiene la unidad de negocio cargada. Cerrá sesión e ingresá de nuevo para actualizar los datos.</p>
        <button @click="handleRelogin" class="mt-4 px-6 py-2 bg-warning-dark text-white text-sm font-semibold rounded-xl hover:bg-warning transition-colors">
          Cerrar sesión
        </button>
      </div>

      <!-- ═══ KPI HERO ═══ -->
      <div v-if="store.loading.kpis" class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="md:col-span-2 bg-white rounded-2xl border border-neutral-200 p-6 animate-pulse">
          <div class="h-4 bg-neutral-200 rounded w-1/3 mb-4"></div>
          <div class="h-10 bg-neutral-200 rounded w-1/2 mb-2"></div>
          <div class="h-3 bg-neutral-100 rounded w-1/4"></div>
        </div>
        <div v-for="i in 4" :key="i" class="bg-white rounded-2xl border border-neutral-200 p-5 animate-pulse">
          <div class="h-3 bg-neutral-200 rounded w-2/3 mb-3"></div>
          <div class="h-7 bg-neutral-200 rounded w-1/2 mb-2"></div>
          <div class="h-2 bg-neutral-100 rounded w-1/3"></div>
        </div>
      </div>

      <template v-else-if="store.kpis.length > 0">
        <!-- Hero KPI card -->
        <div v-if="store.kpiPrincipal" class="bg-linear-to-br from-primary to-primary-dark rounded-2xl shadow-lg p-6 md:p-8 text-white relative overflow-hidden group">
          <div class="absolute right-4 top-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <AppIcon :name="getIconName(store.kpiPrincipal.icono)" class="h-24 w-24 md:h-32 md:w-32" />
          </div>
          <div class="relative z-10">
            <div class="flex items-center gap-2 mb-2">
              <AppIcon :name="getIconName(store.kpiPrincipal.icono)" class="opacity-80" />
              <span class="text-sm font-medium opacity-80 uppercase tracking-wide">{{ store.kpiPrincipal.nombre }}</span>
            </div>
            <div class="flex items-baseline gap-3">
              <span class="text-4xl md:text-5xl font-extrabold" ref="heroValueRef">
                {{ animatedHeroValue }}
              </span>
              <span class="text-lg font-medium opacity-70">{{ store.kpiPrincipal.unidad }}</span>
            </div>
            <div v-if="store.kpiPrincipal.variacion_porcentual != null" class="mt-3 flex items-center gap-1.5">
              <span :class="[
                'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold',
                store.kpiPrincipal.variacion_porcentual >= 0 ? 'bg-white/20 text-white' : 'bg-error-light/20 text-error-light'
              ]">
                <AppIcon :name="store.kpiPrincipal.variacion_porcentual >= 0 ? 'arrowUp' : 'arrowDown'" size="xs" :stroke-width="3" />
                {{ Math.abs(store.kpiPrincipal.variacion_porcentual) }}%
              </span>
              <span class="text-xs opacity-60">vs período anterior</span>
            </div>
          </div>
        </div>

        <!-- Secondary KPIs grid -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-4">
          <div
            v-for="kpi in store.kpisSecundarios"
            :key="kpi.id"
            class="bg-white rounded-2xl border border-neutral-200 p-4 md:p-5 hover:shadow-md hover:border-primary/30 transition-all duration-200 group cursor-default"
          >
            <div class="flex items-center gap-2 mb-2">
              <span class="flex h-8 w-8 items-center justify-center rounded-xl bg-primary-light/20 text-primary group-hover:bg-primary group-hover:text-white transition-colors">
                <AppIcon :name="getIconName(kpi.icono)" size="sm" />
              </span>
              <span class="text-xs font-medium text-neutral-500 leading-tight">{{ kpi.nombre }}</span>
            </div>
            <div class="flex items-baseline gap-1.5">
              <span class="text-xl md:text-2xl font-extrabold text-neutral-900">{{ formatNumber(kpi.valor) }}</span>
              <span class="text-xs font-medium text-neutral-400">{{ kpi.unidad }}</span>
            </div>
            <div v-if="kpi.variacion_porcentual != null" class="mt-1.5">
              <span :class="[
                'text-xs font-semibold',
                kpi.variacion_porcentual >= 0 ? 'text-success' : 'text-error'
              ]">
                {{ kpi.variacion_porcentual >= 0 ? '↑' : '↓' }} {{ Math.abs(kpi.variacion_porcentual) }}%
              </span>
            </div>
          </div>
        </div>
      </template>

      <!-- Empty state -->
      <div v-else-if="!store.loading.kpis" class="bg-white rounded-2xl border border-neutral-200 p-10 text-center">
        <AppIcon name="empty" size="xl" :stroke-width="1.5" class="mx-auto mb-4 h-16 w-16 text-neutral-300" />
        <p class="text-neutral-500 font-medium">No hay datos para los filtros seleccionados</p>
        <p class="text-neutral-400 text-sm mt-1">Probá modificando el rango de fechas o los filtros</p>
      </div>

      <!-- ═══ CHART + RANKING ═══ -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">

        <!-- Evolución temporal -->
        <div class="lg:col-span-3 bg-white rounded-2xl border border-neutral-200 p-5 md:p-6">
          <h2 class="text-sm font-bold text-primary-dark uppercase tracking-wide mb-4">
            {{ store.evolucion.datasets?.[0]?.nombre || 'Evolución' }} — Evolución diaria
          </h2>

          <!-- Loading -->
          <div v-if="store.loading.evolucion" class="h-52 flex items-center justify-center">
            <div class="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>

          <!-- Chart SVG -->
          <div v-else-if="chartPoints.length > 1" class="relative" @mouseleave="tooltip = null">
            <svg :viewBox="`0 0 ${chartW} ${chartH + 30}`" class="w-full" preserveAspectRatio="xMidYMid meet">
              <!-- Grid lines -->
              <line v-for="i in 4" :key="'g'+i"
                :x1="chartPad" :y1="chartH - (chartH - chartPad) * (i/4)" :x2="chartW - chartPad" :y2="chartH - (chartH - chartPad) * (i/4)"
                stroke="var(--color-neutral-200)" stroke-width="0.5" stroke-dasharray="4 4"
              />
              <!-- Y labels -->
              <text v-for="i in 4" :key="'yl'+i"
                :x="chartPad - 4" :y="chartH - (chartH - chartPad) * (i/4) + 3"
                text-anchor="end" fill="var(--color-neutral-400)" font-size="9"
              >{{ formatNumber(maxVal * i / 4) }}</text>
              <!-- Area gradient -->
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.25"/>
                  <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0.02"/>
                </linearGradient>
              </defs>
              <!-- Area -->
              <path :d="areaPath" fill="url(#areaGrad)" />
              <!-- Line -->
              <polyline :points="linePoints" fill="none" stroke="var(--color-primary)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
              <!-- Points -->
              <circle
                v-for="(p, i) in chartPoints" :key="'p'+i"
                :cx="p.x" :cy="p.y" r="4"
                fill="white" stroke="var(--color-primary)" stroke-width="2"
                class="cursor-pointer"
                @mouseenter="tooltip = { x: p.x, y: p.y, label: store.evolucion.labels[i], value: store.evolucion.datasets[0].valores[i] }"
              />
              <!-- X labels (every N) -->
              <text v-for="(p, i) in chartXLabels" :key="'xl'+i"
                :x="p.x" :y="chartH + 20" text-anchor="middle" fill="var(--color-neutral-400)" font-size="8"
              >{{ p.label }}</text>
            </svg>

            <!-- Tooltip -->
            <div v-if="tooltip"
              class="absolute pointer-events-none bg-neutral-900 text-white text-xs rounded-lg px-3 py-1.5 shadow-lg"
              :style="{ left: `${(tooltip.x / chartW) * 100}%`, top: `${(tooltip.y / (chartH + 30)) * 100 - 10}%`, transform: 'translate(-50%, -100%)' }"
            >
              <div class="font-bold">{{ formatNumber(tooltip.value) }}</div>
              <div class="text-neutral-400 text-[10px]">{{ tooltip.label }}</div>
            </div>
          </div>

          <!-- Empty -->
          <div v-else class="h-52 flex items-center justify-center text-neutral-400 text-sm">
            Sin datos de evolución para el período
          </div>
        </div>

        <!-- Ranking Máquinas -->
        <div class="lg:col-span-2 bg-white rounded-2xl border border-neutral-200 p-5 md:p-6">
          <h2 class="text-sm font-bold text-primary-dark uppercase tracking-wide mb-4">Ranking de Máquinas</h2>

          <div v-if="store.loading.ranking" class="space-y-4">
            <div v-for="i in 5" :key="i" class="animate-pulse">
              <div class="h-3 bg-neutral-200 rounded w-2/3 mb-2"></div>
              <div class="h-5 bg-neutral-100 rounded"></div>
            </div>
          </div>

          <div v-else-if="store.rankingMaquinas.length > 0" class="space-y-3">
            <div
              v-for="(item, idx) in store.rankingMaquinas"
              :key="idx"
              class="group"
            >
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2 min-w-0">
                  <span :class="[
                    'shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                    idx === 0 ? 'bg-primary text-white' : idx === 1 ? 'bg-primary-light/40 text-primary-dark' : idx === 2 ? 'bg-neutral-200 text-neutral-600' : 'bg-neutral-100 text-neutral-500'
                  ]">{{ idx + 1 }}</span>
                  <div class="min-w-0">
                    <p class="text-sm font-bold text-neutral-800 truncate">{{ item.patente }}</p>
                    <p class="text-[11px] text-neutral-400 truncate">{{ item.detalle }}</p>
                  </div>
                </div>
                <div class="text-right shrink-0 ml-2">
                  <span class="text-sm font-extrabold text-neutral-900">{{ formatNumber(item.valor) }}</span>
                  <span class="text-[10px] text-neutral-400 block">{{ item.registros }} reg.</span>
                </div>
              </div>
              <!-- Progress bar -->
              <div class="h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="idx === 0 ? 'bg-primary' : 'bg-primary-light'"
                  :style="{ width: `${rankingMaxVal > 0 ? (item.valor / rankingMaxVal * 100) : 0}%` }"
                ></div>
              </div>
            </div>
          </div>

          <div v-else class="h-40 flex items-center justify-center text-neutral-400 text-sm">
            Sin datos de ranking
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import AutocompleteField from '@/components/AutocompleteField.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const authStore = useAuthStore()
const store = useDashboardStore()
const router = useRouter()

const showFilters = ref(false)
const tooltip = ref(null)

const tipoProcesoFilter = computed({
  get: () => store.filtros.tipo_proceso_id || '',
  set: (value) => store.setFiltro('tipo_proceso_id', value ? Number(value) : null),
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

function handleRelogin() {
  authStore.logout()
  router.push({ name: 'login' })
}

// ─── Animated hero value ───
const animatedHeroValue = ref('0')
const heroValueRef = ref(null)

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
  if (newVal != null) {
    animateValue(oldVal || 0, newVal)
  }
})

// ─── Icon mapping ───
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

function getIconName(name) {
  return iconMap[name] || 'empty'
}

// ─── Number formatting ───
function formatNumber(val) {
  if (val == null) return '0'
  const n = Number(val)
  if (isNaN(n)) return '0'
  if (Number.isInteger(n)) return n.toLocaleString('es-AR')
  return n.toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 2 })
}

// ─── Chart computations ───
const chartW = 600
const chartH = 200
const chartPad = 40

const maxVal = computed(() => {
  const vals = store.evolucion.datasets?.[0]?.valores || []
  return Math.max(...vals, 1)
})

const chartPoints = computed(() => {
  const vals = store.evolucion.datasets?.[0]?.valores || []
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
  const labels = store.evolucion.labels || []
  const pts = chartPoints.value
  if (pts.length === 0) return []
  // Show max ~8 labels
  const step = Math.max(1, Math.ceil(labels.length / 8))
  return labels.reduce((acc, label, i) => {
    if (i % step === 0 && pts[i]) {
      const short = label.length > 5 ? label.slice(5) : label // "MM-DD"
      acc.push({ x: pts[i].x, label: short })
    }
    return acc
  }, [])
})

// ─── Ranking ───
const rankingMaxVal = computed(() => {
  if (store.rankingMaquinas.length === 0) return 1
  return Math.max(...store.rankingMaquinas.map((r) => r.valor), 1)
})

// ─── Init ───
const missingUn = ref(false)

onMounted(async () => {
  const unId = authStore.user?.unidad_negocio
  if (!unId) {
    missingUn.value = true
    return
  }

  store.initFiltros(unId)
  await store.loadTiposProceso(unId)
  await store.loadMovilesDisponibles(unId)
  await store.fetchAll()

  // Animate initial hero value
  await nextTick()
  if (store.kpiPrincipal?.valor) {
    animateValue(0, store.kpiPrincipal.valor)
  }
})
</script>
