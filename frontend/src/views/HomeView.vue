<template>
  <div class="min-h-[calc(100vh-8.5rem)] bg-[var(--app-bg)] px-3 py-3 pb-20 md:min-h-screen md:px-4 md:py-4">
    <div class="mx-auto w-full max-w-[112rem] space-y-3">
      <section class="app-card-glass rounded-xl px-4 py-3 md:px-5">
        <div class="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div class="min-w-0">
            <div class="mb-2 flex flex-wrap items-center gap-2">
              <span :class="['inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[11px] font-extrabold uppercase', isOnline ? 'app-chip-success' : 'app-chip-warning']">
                <span :class="['app-led h-2 w-2 rounded-full', isOnline ? 'bg-primary text-primary' : 'bg-warning text-warning']"></span>
                {{ isOnline ? 'En línea' : 'Sin conexión' }}
              </span>
              <span class="rounded-full border px-3 py-1 text-xs font-bold app-chip-info">{{ isAdmin ? 'Administrador' : roleLabel }}</span>
              <span class="rounded-full border px-3 py-1 text-xs font-bold app-state-inactive">{{ todayLabel }}</span>
            </div>
            <h1 class="truncate text-3xl font-extrabold leading-none text-neutral-950 md:text-[2.5rem]">
              {{ isAdmin ? 'Panel operativo' : authStore.userName }}
            </h1>
            <p class="mt-1 text-sm font-medium text-neutral-500">
              {{ headerSubtitle }}
            </p>
          </div>

          <div class="flex flex-col gap-2 xl:items-end">
            <div class="flex flex-wrap gap-2">
              <button
                v-for="preset in datePresets"
                :key="preset.key"
                type="button"
                :class="[
                  'rounded-lg border px-3 py-2 text-xs font-bold transition active:scale-[0.98]',
                  selectedDatePreset === preset.key
                    ? 'border-primary/55 bg-primary/20 text-primary-dark'
                    : 'app-button-soft border',
                ]"
                @click="selectDatePreset(preset.key)"
              >
                {{ preset.label }}
              </button>
              <label class="app-input flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-bold">
                Fecha
                <input
                  v-model="selectedDate"
                  type="date"
                  class="bg-transparent text-xs font-bold text-neutral-900 outline-none"
                  @change="selectCustomDate"
                />
              </label>
            </div>
            <div class="grid grid-cols-1 gap-2 sm:grid-cols-3 xl:min-w-[45rem]">
            <button
              v-for="action in topActions"
              :key="action.name"
              type="button"
              class="app-hover-glow inline-flex min-h-11 items-center justify-center gap-3 rounded-lg border border-primary/35 bg-primary-light/20 px-3 py-2 text-left text-sm font-extrabold text-neutral-800 transition active:scale-[0.98]"
              @click="router.push(action.to)"
            >
              <span class="truncate">{{ action.label }}</span>
              <AppIcon :name="action.icon" size="sm" class="shrink-0" />
            </button>
            </div>
          </div>
        </div>
      </section>

      <template v-if="isAdmin">
        <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricTile v-for="card in adminSummaryCards" :key="card.label" :card="card" :loading="adminStore.loading" />
        </section>

        <section class="grid gap-3 xl:grid-cols-[minmax(0,1fr)_30rem]">
          <article class="app-card overflow-hidden rounded-xl p-0">
            <div class="flex items-center justify-between gap-3 px-4 pb-2 pt-4 md:px-5">
              <div>
                <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Unidades de negocio</p>
                <h2 class="mt-1 text-2xl font-extrabold leading-tight text-neutral-900">Última actividad registrada</h2>
              </div>
              <span class="app-surface-muted hidden h-9 w-9 items-center justify-center rounded-lg border text-neutral-500 sm:flex">
                <AppIcon name="unit" size="sm" />
              </span>
            </div>

            <div class="grid gap-3 px-4 py-3 md:grid-cols-[minmax(0,1fr)_auto] md:items-center md:px-5">
              <label class="relative block">
                <span class="sr-only">Buscar unidad de negocio</span>
                <AppIcon name="search" size="sm" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" />
                <input
                  v-model="unitSearch"
                  type="search"
                  class="app-input w-full rounded-lg border py-2.5 pl-10 pr-3 text-sm font-semibold placeholder:text-neutral-400 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20"
                  placeholder="Buscar por nombre o prefijo"
                />
              </label>
              <div class="flex flex-wrap gap-2 text-xs font-extrabold">
                <span class="rounded-lg border px-3 py-2 app-state-active">{{ adminTotals.unidadesActivas }} con actividad</span>
                <span class="rounded-lg border px-3 py-2 app-state-idle">{{ inactiveUnits.length }} sin actividad registrada</span>
              </div>
            </div>

            <div v-if="adminStore.loading" class="grid gap-3 px-4 py-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 md:px-5">
              <div v-for="i in 12" :key="i" class="app-surface-muted h-16 animate-pulse rounded-lg"></div>
            </div>

            <div v-else-if="pagedAdminUnits.length > 0" class="grid gap-3 px-4 py-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 md:px-5">
              <button
                v-for="unidad in pagedAdminUnits"
                :key="unidad.id"
                type="button"
                :class="[
                  'group grid min-h-[5.35rem] grid-cols-[auto_minmax(0,1fr)] items-start gap-3 overflow-hidden rounded-lg border p-3 text-left transition duration-150 ease-out hover:-translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 active:translate-y-0 active:scale-[0.99]',
                  unitCardClass(unidad),
                ]"
                @click="router.push({ name: 'admin-dashboard' })"
              >
                <span :class="['flex h-9 min-w-9 items-center justify-center rounded-md border px-2 text-xs font-extrabold', unitStatusClass(unidad)]">
                  {{ unidad.prefijo || 'SIN' }}
                </span>
                <div class="min-w-0">
                  <p class="truncate text-sm font-extrabold text-neutral-900">{{ unidad.nombre }}</p>
                  <p class="mt-0.5 flex items-center gap-1.5 text-xs font-medium text-neutral-500">
                    <span :class="['h-1.5 w-1.5 rounded-full', unitDotClass(unidad)]"></span>
                    {{ unitStatusText(unidad) }}
                  </p>
                  <template v-if="unidad.resumen?.ultima_actividad_fecha">
                    <p class="mt-1.5 flex min-w-0 max-w-full items-center overflow-hidden text-[11px] text-neutral-400">
                      Última: {{ formatFecha(unidad.resumen.ultima_actividad_fecha) }}
                      <span v-if="unidad.resumen.ultima_actividad_resumen" class="ml-1">-</span>
                      <span v-if="unidad.resumen.ultima_actividad_resumen" class="min-w-0 flex-1 truncate">{{ unidad.resumen.ultima_actividad_resumen }}</span>
                    </p>
                  </template>
                  <template v-else>
                    <p class="mt-1.5 text-[11px] text-neutral-400">Sin actividad registrada</p>
                  </template>
                </div>
              </button>
            </div>
            <div v-else class="px-5 py-10 text-center">
              <p class="text-sm font-bold text-neutral-700">No hay unidades para esa búsqueda.</p>
              <button type="button" class="mt-2 text-xs font-bold text-primary-dark underline underline-offset-4" @click="unitSearch = ''">
                Limpiar búsqueda
              </button>
            </div>

            <div v-if="adminUnits.length > 0" class="flex flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between md:px-5">
              <p class="text-xs font-semibold text-neutral-400">
                Mostrando {{ adminUnitDisplayStart }}-{{ adminUnitPageEnd }} de {{ filteredAdminUnits.length }} unidades
              </p>
              <div class="flex items-center gap-2">
                <button
                  type="button"
                  class="rounded-lg border border-neutral-200 px-3 py-2 text-xs font-bold text-neutral-600 transition hover:border-primary/35 hover:text-primary-dark disabled:cursor-not-allowed disabled:opacity-40"
                  :disabled="adminUnitPage === 1"
                  @click="adminUnitPage = Math.max(1, adminUnitPage - 1)"
                >
                  Anterior
                </button>
                <span class="rounded-lg border px-3 py-2 text-xs font-extrabold app-state-inactive">
                  {{ adminUnitPage }} / {{ adminUnitTotalPages }}
                </span>
                <button
                  type="button"
                  class="rounded-lg border border-neutral-200 px-3 py-2 text-xs font-bold text-neutral-600 transition hover:border-primary/35 hover:text-primary-dark disabled:cursor-not-allowed disabled:opacity-40"
                  :disabled="adminUnitPage === adminUnitTotalPages"
                  @click="adminUnitPage = Math.min(adminUnitTotalPages, adminUnitPage + 1)"
                >
                  Siguiente
                </button>
              </div>
            </div>
          </article>

          <aside class="space-y-3">
            <AlertPanel
              :alerts="adminAlerts"
              :unit-labels="inactiveUnitLabels"
              action-label="Abrir Dashboard Operativo"
              @action="router.push({ name: 'admin-dashboard' })"
            />
            <RecentRecordsPanel />
            <QuickActions
              :actions="adminActions"
              :show-install="Boolean(pwaInstall?.deferredInstallPrompt?.value)"
              @install="pwaInstall?.installApp"
            />
          </aside>
        </section>
      </template>

      <template v-else>
        <section class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <button
            v-for="action in operatorMainActions"
            :key="action.name"
            type="button"
            class="group app-card rounded-xl p-4 text-left transition hover:-translate-y-px hover:border-secondary/35 hover:shadow-md"
            @click="router.push(action.to)"
          >
            <div class="mb-4 flex items-center justify-between gap-3">
              <span class="flex h-11 w-11 items-center justify-center rounded-lg bg-primary-dark text-white">
                <AppIcon :name="action.icon" size="sm" />
              </span>
              <span v-if="Number(action.badge || 0) > 0" class="rounded-full bg-warning px-2 py-0.5 text-xs font-extrabold text-white">{{ action.badge }}</span>
            </div>
            <h2 class="text-base font-extrabold text-neutral-900 group-hover:text-info-dark">{{ action.label }}</h2>
            <p class="mt-1 text-sm font-medium text-neutral-500">{{ action.description }}</p>
          </button>
        </section>

        <section v-if="!recordsStore.loading && !lastRecord" class="rounded-xl border border-dashed border-warning/40 bg-warning-light/20 p-4">
          <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p class="text-xs font-extrabold uppercase tracking-wide text-neutral-400">{{ emptyRangeEyebrow }}</p>
              <h2 class="mt-1 text-xl font-extrabold text-neutral-900">{{ emptyRangeTitle }}</h2>
              <p class="mt-1 text-sm text-neutral-500">Podés iniciar una carga productiva o registrar combustible directamente.</p>
            </div>
            <div class="flex flex-col gap-2 sm:flex-row">
              <button type="button" class="min-h-10 rounded-lg bg-primary px-4 py-2 text-sm font-extrabold text-on-primary" @click="router.push({ name: 'produccion' })">Ir a Carga de Producción</button>
              <button type="button" class="app-button-soft rounded-lg border px-4 py-2.5 text-sm font-extrabold" @click="router.push({ name: 'combustible' })">Ir a Carga de Combustible</button>
            </div>
          </div>
        </section>

        <section class="grid gap-3 xl:grid-cols-[minmax(0,1fr)_22rem]">
          <div class="space-y-3">
            <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <MetricTile v-for="card in operatorSummaryCards" :key="card.label" :card="card" :loading="recordsStore.loading" />
            </div>
            <LastPersonalRecord />
          </div>

          <aside class="space-y-3">
            <SyncCard />
            <QuickActions
              :actions="operatorSecondaryActions"
              :show-install="Boolean(pwaInstall?.deferredInstallPrompt?.value)"
              @install="pwaInstall?.installApp"
            />
          </aside>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, inject, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import { useMisRegistrosStore } from '@/stores/misRegistros'
import { useAdminStore } from '@/stores/admin'
import AppIcon from '@/components/ui/AppIcon.vue'

const authStore = useAuthStore()
const produccionStore = useProduccionStore()
const recordsStore = useMisRegistrosStore()
const adminStore = useAdminStore()
const router = useRouter()
const pwaInstall = inject('pwaInstall', null)
const isOnline = ref(navigator.onLine)
const selectedDatePreset = ref('today')
const selectedDate = ref(formatDateInput(new Date()))
const unitSearch = ref('')
const adminUnitPage = ref(1)
const adminUnitsPerPage = 12
const MAX_ALERT_UNIT_LABELS = 12

const datePresets = [
  { key: 'today', label: 'Hoy' },
  { key: 'yesterday', label: 'Ayer' },
  { key: 'last7', label: '7 días' },
  { key: 'lastWeek', label: 'Semana pasada' },
]

const isAdmin = computed(() => authStore.isAdmin)

const selectedDateRange = computed(() => {
  const today = startOfDay(new Date())
  if (selectedDatePreset.value === 'yesterday') {
    const day = addDays(today, -1)
    return { from: formatDateInput(day), to: formatDateInput(day) }
  }
  if (selectedDatePreset.value === 'last7') {
    return { from: formatDateInput(addDays(today, -6)), to: formatDateInput(today) }
  }
  if (selectedDatePreset.value === 'lastWeek') {
    const currentDay = today.getDay() || 7
    const lastWeekEnd = addDays(today, -currentDay)
    const lastWeekStart = addDays(lastWeekEnd, -6)
    return { from: formatDateInput(lastWeekStart), to: formatDateInput(lastWeekEnd) }
  }
  return { from: selectedDate.value, to: selectedDate.value }
})

const todayLabel = computed(() => {
  const { from, to } = selectedDateRange.value
  if (from === to) return formatDisplayDate(from)
  return `${formatDisplayDate(from)} - ${formatDisplayDate(to)}`
})

const rangeLabel = computed(() => {
  const { from, to } = selectedDateRange.value
  if (from === to) return formatDisplayDate(from)
  return `${formatDisplayDate(from)} - ${formatDisplayDate(to)}`
})

const isTodayRange = computed(() => selectedDatePreset.value === 'today')

const headerSubtitle = computed(() => {
  if (isAdmin.value) {
    return isTodayRange.value
      ? 'Resumen de hoy y accesos de administración. La sección de unidades muestra la última actividad registrada.'
      : `Resumen de ${rangeLabel.value} y accesos de administración. La sección de unidades muestra la última actividad registrada.`
  }
  return isTodayRange.value
    ? 'Accesos del día, estado de sincronización y actividad personal.'
    : `Accesos de ${rangeLabel.value}, estado de sincronización y actividad personal.`
})

const roleLabel = computed(() => authStore.user?.encargado === 1 ? 'Encargado' : 'Operador')

const topActions = computed(() => isAdmin.value
  ? [
      { name: 'admin-dashboard', label: 'Abrir Dashboard', icon: 'dashboard', to: { name: 'admin-dashboard' } },
      { name: 'produccion', label: 'Carga Producción', icon: 'production', to: { name: 'produccion' } },
      { name: 'combustible', label: 'Carga Combustible', icon: 'fuel', to: { name: 'combustible' } },
    ]
  : operatorMainActions.value.slice(0, 2))

const operatorMainActions = computed(() => [
  { name: 'produccion', label: 'Ir a Carga de Producción', description: 'Abre el formulario de producción.', icon: 'production', to: { name: 'produccion' } },
  { name: 'combustible', label: 'Ir a Carga de Combustible', description: 'Abre el formulario de combustible.', icon: 'fuel', to: { name: 'combustible' } },
  { name: 'pendientes', label: 'Ver Pendientes', description: 'Abre cola offline y reintentos.', icon: 'pending', to: { name: 'pendientes' }, badge: produccionStore.pendingCount },
  authStore.user?.encargado === 1
    ? { name: 'dashboard', label: 'Abrir Dashboard Operativo', description: 'Abre resumen por unidad y proceso.', icon: 'dashboard', to: { name: 'dashboard' } }
    : { name: 'mis-registros', label: 'Abrir Mis Registros', description: 'Abre historial y totales personales.', icon: 'records', to: { name: 'mis-registros' } },
])

const operatorSecondaryActions = computed(() => [
  { name: 'pendientes', label: 'Abrir Pendientes', description: 'Cola offline y reintentos.', to: { name: 'pendientes' }, badge: produccionStore.pendingCount },
  authStore.user?.encargado === 1
    ? { name: 'dashboard', label: 'Abrir Dashboard Operativo', description: 'Resumen por unidad y proceso.', to: { name: 'dashboard' }, badge: null }
    : { name: 'mis-registros', label: 'Abrir Mis Registros', description: 'Historial y totales personales.', to: { name: 'mis-registros' }, badge: null },
])

const adminActions = computed(() => [
  { name: 'produccion', label: 'Ir a Carga de Producción', description: 'Abre el formulario de producción.', to: { name: 'produccion' }, badge: null },
  { name: 'combustible', label: 'Ir a Carga de Combustible', description: 'Abre el formulario de combustible.', to: { name: 'combustible' }, badge: null },
  { name: 'pendientes', label: 'Abrir Pendientes', description: 'Cola offline y reintentos.', to: { name: 'pendientes' }, badge: produccionStore.pendingCount },
  { name: 'admin', label: 'Abrir Panel Admin', description: 'Catálogos, permisos y relaciones.', to: { name: 'admin-dashboard' }, badge: null },
])

const adminTotals = computed(() => adminStore.dashboard.reduce((acc, unidad) => {
  const resumen = unidad.resumen || {}
  acc.registros += Number(resumen.total_registros || 0)
  acc.produccion += Number(resumen.produccion_total || 0)
  acc.combustible += Number(resumen.combustible_total || 0)
  acc.operadores += Number(resumen.operadores_activos || 0)
  const tieneActividad = (resumen.total_registros || 0) > 0 || resumen.ultima_actividad_fecha
  if (tieneActividad) acc.unidadesActivas += 1
  return acc
}, { registros: 0, produccion: 0, combustible: 0, operadores: 0, unidadesActivas: 0 }))

const adminUnits = computed(() => [...adminStore.dashboard].sort(compareUnitsByLastActivity))
const inactiveUnits = computed(() => adminUnits.value.filter((unidad) => {
  const resumen = unidad.resumen || {}
  return (resumen.total_registros || 0) === 0 && !resumen.ultima_actividad_fecha
}))
const normalizedUnitSearch = computed(() => normalizeSearch(unitSearch.value))
const filteredAdminUnits = computed(() => {
  const query = normalizedUnitSearch.value
  if (!query) return adminUnits.value
  return adminUnits.value.filter((unidad) => {
    const haystack = normalizeSearch(`${unidad.prefijo || ''} ${unidad.nombre || ''} ${unitStatusText(unidad)}`)
    return haystack.includes(query)
  })
})
const adminUnitTotalPages = computed(() => Math.max(1, Math.ceil(filteredAdminUnits.value.length / adminUnitsPerPage)))
const adminUnitPageStart = computed(() => filteredAdminUnits.value.length === 0 ? 0 : (adminUnitPage.value - 1) * adminUnitsPerPage)
const adminUnitPageEnd = computed(() => Math.min(adminUnitPageStart.value + adminUnitsPerPage, filteredAdminUnits.value.length))
const adminUnitDisplayStart = computed(() => filteredAdminUnits.value.length === 0 ? 0 : adminUnitPageStart.value + 1)
const pagedAdminUnits = computed(() => filteredAdminUnits.value.slice(adminUnitPageStart.value, adminUnitPageEnd.value))

const adminSummaryCards = computed(() => [
  { label: 'Producción total periodo', value: fmt(adminTotals.value.produccion), detail: 'Todas las unidades', icon: 'production' },
  { label: 'Registros periodo', value: fmt(adminTotals.value.registros), detail: 'Cargas del sistema', icon: 'records' },
  { label: 'Unidades con actividad', value: `${adminTotals.value.unidadesActivas} / ${adminUnits.value.length}`, detail: inactiveUnits.value.length ? `${inactiveUnits.value.length} sin actividad registrada` : 'Todas con actividad', icon: 'unit' },
  { label: 'Pendientes offline', value: fmt(produccionStore.pendingCount), detail: syncText.value, icon: 'pending' },
])

const adminAlerts = computed(() => {
  const alerts = []
  if (!isOnline.value) alerts.push('Sistema sin conexión: las cargas quedan en cola local.')
  if (produccionStore.pendingCount > 0) alerts.push(`${produccionStore.pendingCount} registro(s) pendientes de sincronización.`)
  if (inactiveUnits.value.length > 0) {
    alerts.push(`${inactiveUnits.value.length} unidades sin actividad registrada.`)
  }
  if (alerts.length === 0) alerts.push('Sin alertas operativas.')
  return alerts
})

const inactiveUnitLabels = computed(() => {
  const labels = inactiveUnits.value.map((unidad) => unidad.prefijo || unidad.nombre || 'SIN')
  if (labels.length <= MAX_ALERT_UNIT_LABELS) return labels
  return [...labels.slice(0, MAX_ALERT_UNIT_LABELS), `+${labels.length - MAX_ALERT_UNIT_LABELS}`]
})

watch([normalizedUnitSearch, adminUnits], () => {
  adminUnitPage.value = 1
})

watch(adminUnitTotalPages, (totalPages) => {
  if (adminUnitPage.value > totalPages) adminUnitPage.value = totalPages
})

const productionToday = computed(() => {
  const totals = recordsStore.totales
  const options = [
    { label: 'Metros cubicos', value: totals.total_m3, unit: 'm3' },
    { label: 'Toneladas', value: totals.total_tn, unit: 'TN' },
    { label: 'Hectareas', value: totals.total_has, unit: 'HAS' },
    { label: 'Carros', value: totals.total_carros, unit: 'uds' },
    { label: 'Plantas', value: totals.total_plantas, unit: 'uds' },
    { label: 'KM carreteo', value: totals.total_km_carreteo, unit: 'km' },
    { label: 'KM perfilado', value: totals.total_km_perfilado, unit: 'km' },
  ]
  return options.find((item) => Number(item.value) > 0) || { label: 'Producción', value: 0, unit: '' }
})

const sortedRecords = computed(() => [...recordsStore.registros].sort((a, b) => {
  const dateDiff = String(b.fecha || '').localeCompare(String(a.fecha || ''))
  if (dateDiff !== 0) return dateDiff
  return Number(b.id || 0) - Number(a.id || 0)
}))

const lastRecord = computed(() => sortedRecords.value[0] || null)
const lastRecordEyebrow = computed(() => {
  return isTodayRange.value
    ? 'Último registro del día'
    : `Último registro del periodo (${rangeLabel.value})`
})
const lastRecordTitle = computed(() => {
  if (lastRecord.value) return lastRecord.value.operacion
  return isTodayRange.value ? 'Sin actividad hoy' : 'Sin registros en el periodo'
})
const emptyRangeEyebrow = computed(() => {
  return isTodayRange.value
    ? 'Sin actividad hoy'
    : `Sin registros en ${rangeLabel.value}`
})
const emptyRangeTitle = computed(() => {
  return isTodayRange.value
    ? 'Todavía no cargaste registros.'
    : 'No hay registros en el periodo seleccionado.'
})

const lastRecordMetrics = computed(() => {
  const record = lastRecord.value
  if (!record) return []
  return [
    { label: 'tn', value: record.tn_despachadas, unit: 'TN' },
    { label: 'm3', value: record.m3, unit: 'm3' },
    { label: 'has', value: record.has, unit: 'HAS' },
    { label: 'carros', value: record.carros, unit: 'carros' },
    { label: 'combustible', value: record.combustible, unit: 'lts' },
  ].filter((item) => Number(item.value) > 0).map((item) => ({ ...item, value: fmt(item.value) }))
})

const rangeShortLabel = computed(() => {
  switch (selectedDatePreset.value) {
    case 'today':
      return 'hoy'
    case 'yesterday':
      return 'ayer'
    case 'last7':
      return 'ultimos 7 dias'
    case 'lastWeek':
      return 'semana pasada'
    default:
      return 'este periodo'
  }
})

const rangeLongLabel = computed(() => {
  if (selectedDatePreset.value !== 'custom') return rangeShortLabel.value
  return `del ${rangeLabel.value}`
})

const operatorSummaryCards = computed(() => [
  {
    label: 'Produccion',
    value: fmt(productionToday.value.value),
    unit: productionToday.value.unit,
    detail: `${productionToday.value.label} (${rangeShortLabel.value})`,
    icon: 'production',
  },
  { label: 'Horas', value: fmt(recordsStore.totales.total_horas), unit: 'hs', detail: 'Tiempo trabajado', icon: 'timer' },
  {
    label: 'Registros',
    value: fmt(recordsStore.totales.total),
    detail: `Cargas ${rangeShortLabel.value}`,
    icon: 'records',
  },
  { label: 'Combustible', value: fmt(recordsStore.totales.total_combustible), unit: 'lts', detail: 'Consumo cargado', icon: 'fuel' },
])

const syncText = computed(() => {
  if (!isOnline.value) return 'Sin conexión'
  if (produccionStore.syncingPending) return 'Sincronizando'
  if (produccionStore.pendingCount > 0) return 'Con pendientes'
  return 'Todo sincronizado'
})

const MetricTile = defineComponent({
  props: {
    card: { type: Object, required: true },
    loading: { type: Boolean, default: false },
  },
  setup(props) {
    return () => h('article', { class: 'app-card app-hover-glow grid min-h-[6.7rem] grid-cols-[auto_minmax(0,1fr)] items-center gap-4 rounded-xl p-4' }, [
      h('span', { class: 'flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-primary/30 bg-primary-light/30 text-info shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)]' }, [
        h(AppIcon, { name: props.card.icon || 'dashboard', size: 'lg', class: props.card.icon === 'fuel' ? 'text-warning-dark' : 'text-info' }),
      ]),
      h('div', { class: 'min-w-0' }, [
        h('p', { class: 'truncate text-xs font-bold uppercase tracking-wide text-neutral-400' }, props.card.label),
        h('div', { class: 'mt-1 flex items-baseline gap-1.5' }, [
          h('span', { class: 'text-3xl font-extrabold leading-none text-neutral-950' }, props.loading ? '-' : props.card.value),
          props.card.unit ? h('span', { class: 'text-xs font-bold text-neutral-400' }, props.card.unit) : null,
        ]),
        h('p', { class: 'mt-1 truncate text-xs font-medium text-neutral-400' }, props.card.detail || ''),
      ]),
    ])
  },
})

const QuickActions = defineComponent({
  props: {
    actions: { type: Array, required: true },
    showInstall: { type: Boolean, default: false },
  },
  emits: ['install'],
  setup(props, { emit }) {
    return () => h('article', { class: 'app-card rounded-xl p-4' }, [
      h('div', { class: 'mb-3' }, [
        h('p', { class: 'text-xs font-bold uppercase tracking-wide text-neutral-400' }, 'Accesos rapidos'),
        h('h2', { class: 'mt-0.5 text-xl font-extrabold text-neutral-900' }, 'Operaciones'),
      ]),
      h('div', { class: 'grid gap-1.5' }, [
        ...props.actions.map((action) => h('button', {
          key: action.name,
          type: 'button',
          class: 'app-hover-glow app-surface-muted flex w-full items-center justify-between gap-3 rounded-lg border px-3 py-2.5 text-left transition active:scale-[0.98]',
          onClick: () => router.push(action.to),
        }, [
          h('span', { class: 'min-w-0' }, [
            h('span', { class: 'block truncate text-sm font-bold text-neutral-800' }, action.label),
          ]),
          action.badge !== null ? h('span', { class: 'rounded-md bg-warning-light px-2 py-0.5 text-xs font-extrabold text-warning-dark' }, String(action.badge)) : h(AppIcon, { name: 'forward', size: 'xs', class: 'text-neutral-400' }),
        ])),
        props.showInstall ? h('button', {
          type: 'button',
          class: 'app-hover-glow app-surface-muted flex w-full items-center justify-between gap-3 rounded-lg border px-3 py-2.5 text-left transition active:scale-[0.98]',
          onClick: () => emit('install'),
        }, h('span', [
          h('span', { class: 'block text-sm font-bold text-neutral-800' }, 'Instalar app'),
          h('span', { class: 'block text-xs text-neutral-400' }, 'Acceso rapido y soporte offline.'),
        ])) : null,
      ]),
    ])
  },
})

const LastPersonalRecord = defineComponent({
  setup() {
    return () => h('article', { class: 'app-card rounded-xl p-4' }, [
      h('div', { class: 'mb-3 flex items-center justify-between gap-3' }, [
        h('div', [
          h('p', { class: 'text-xs font-bold uppercase tracking-wide text-neutral-400' }, lastRecordEyebrow.value),
          h('h2', { class: 'mt-1 text-lg font-extrabold text-neutral-900' }, lastRecordTitle.value),
        ]),
        h(AppIcon, { name: 'records', size: 'lg', class: 'text-info' }),
      ]),
      recordsStore.loading
        ? h('div', { class: 'space-y-2' }, [h('div', { class: 'app-surface-muted h-4 w-2/3 animate-pulse rounded' }), h('div', { class: 'app-surface-muted h-4 w-1/2 animate-pulse rounded' })])
        : lastRecord.value
          ? h('div', { class: 'space-y-3' }, [
            h('p', { class: 'text-sm text-neutral-500' }, `${formatFecha(lastRecord.value.fecha)} - ${lastRecord.value.equipo || 'Sin equipo'} - ${horaRegistro(lastRecord.value)}`),
            h('div', { class: 'flex flex-wrap gap-2' }, lastRecordMetrics.value.map((metric) => h('span', { key: metric.label, class: 'rounded-md border px-2.5 py-1 text-xs font-bold app-state-inactive' }, `${metric.value} ${metric.unit}`))),
            h('button', { type: 'button', class: 'rounded-md border border-neutral-200 px-3 py-2 text-xs font-bold text-neutral-700 hover:border-secondary/40 hover:text-info-dark', onClick: () => router.push({ name: 'mis-registros' }) }, 'Ver mis registros'),
          ])
          : h('p', { class: 'text-sm text-neutral-500' }, isTodayRange.value ? 'Todavia no hay registros cargados para hoy.' : 'No hay registros cargados en este periodo.'),
    ])
  },
})

const SyncCard = defineComponent({
  setup() {
    return () => h('article', { class: 'app-card rounded-xl p-4' }, [
      h('div', { class: 'mb-3 flex items-center justify-between gap-3' }, [
        h('div', [
          h('p', { class: 'text-xs font-bold uppercase tracking-wide text-neutral-400' }, 'Sincronizacion'),
          h('h2', { class: 'mt-1 text-lg font-extrabold text-neutral-900' }, `${produccionStore.pendingCount} pendiente${produccionStore.pendingCount !== 1 ? 's' : ''}`),
        ]),
        h(AppIcon, { name: isOnline.value ? 'online' : 'offline', size: 'lg', class: isOnline.value ? 'text-success' : 'text-warning-dark' }),
      ]),
      h('p', { class: 'text-sm text-neutral-500' }, syncText.value),
    ])
  },
})

const AlertPanel = defineComponent({
  props: {
    alerts: { type: Array, required: true },
    unitLabels: { type: Array, default: () => [] },
    actionLabel: { type: String, default: 'Abrir detalle' },
  },
  emits: ['action'],
  setup(props, { emit }) {
    return () => h('article', { class: 'rounded-xl border border-error/45 bg-error-light p-4 shadow-sm' }, [
      h('div', { class: 'mb-3 flex items-center justify-between gap-3' }, [
        h('div', [
          h('p', { class: 'text-xs font-bold uppercase tracking-wide text-error-dark/80' }, 'Alertas operativas'),
          h('h2', { class: 'mt-1 text-2xl font-extrabold leading-none text-error-dark' }, `${props.alerts.length} alerta${props.alerts.length !== 1 ? 's' : ''}`),
        ]),
        h(AppIcon, { name: 'warning', size: 'lg', class: 'text-error-dark opacity-80' }),
      ]),
      h('div', { class: 'space-y-2' }, props.alerts.map((alert) => h('p', { key: alert, class: 'rounded-lg border border-error/25 bg-error-light/30 px-3 py-2 text-sm font-semibold text-error-dark' }, alert))),
      props.unitLabels.length > 0
        ? h('div', { class: 'mt-3 rounded-lg p-0' }, [
          h('p', { class: 'mb-2 text-[11px] font-bold uppercase tracking-wide text-error-dark/70' }, 'Unidades afectadas'),
          h('div', { class: 'flex flex-wrap gap-1.5' }, props.unitLabels.map((label) => h('span', { key: label, class: 'rounded-md border border-error/40 bg-error-light px-2.5 py-1 text-xs font-bold text-error-dark' }, label))),
        ])
        : null,
      h('button', {
        type: 'button',
        class: 'mt-4 inline-flex w-full items-center justify-center rounded-lg bg-error px-3 py-2.5 text-sm font-extrabold text-white transition hover:bg-error-dark active:scale-[0.98]',
        onClick: () => emit('action'),
      }, props.actionLabel),
    ])
  },
})

const RecentRecordsPanel = defineComponent({
  setup() {
    return () => h('article', { class: 'app-card rounded-xl p-4' }, [
      h('div', { class: 'mb-3' }, [
        h('p', { class: 'text-xs font-bold uppercase tracking-wide text-neutral-400' }, 'Ultimos registros'),
        h('h2', { class: 'mt-0.5 text-xl font-extrabold text-neutral-900' }, 'Ultimas cargas'),
      ]),
      adminStore.loadingRecentRecords
        ? h('div', { class: 'space-y-2' }, [1, 2, 3].map((i) => h('div', { key: i, class: 'app-surface-muted h-12 animate-pulse rounded-lg' })))
        : adminStore.recentRecords.length > 0
          ? h('div', { class: 'divide-y divide-neutral-100' }, adminStore.recentRecords.map((record) => h('div', { key: record.id, class: 'py-3' }, [
            h('p', { class: 'truncate text-sm font-bold text-neutral-800' }, `${record.operacion || 'Producción'} - ${record.unidad || 'Sin unidad'}`),
            h('p', { class: 'truncate text-xs text-neutral-400' }, `${formatFecha(record.fecha)} - ${record.operador || 'Sin operador'} - ${record.equipo || 'Sin equipo'}`),
          ])))
          : h('p', { class: 'text-sm text-neutral-500' }, 'Sin registros cargados.'),
    ])
  },
})

function fmt(val) {
  const n = Number(val || 0)
  return n.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function normalizeSearch(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toLowerCase()
}

function formatFecha(fecha) {
  if (!fecha) return '-'
  const [y, m, d] = String(fecha).split('-')
  if (!y || !m || !d) return fecha
  return `${d}/${m}/${y}`
}

function horaRegistro(record) {
  if (record?.hr_fin) return String(record.hr_fin)
  if (record?.hr_inicio) return String(record.hr_inicio)
  return '-'
}

function unitStatusClass(unidad) {
  const tieneActividad = (unidad.resumen?.total_registros || 0) > 0 || unidad.resumen?.ultima_actividad_fecha
  if (tieneActividad) return 'app-state-active'
  return 'app-state-idle'
}

function unitCardClass(unidad) {
  const tieneActividad = (unidad.resumen?.total_registros || 0) > 0 || unidad.resumen?.ultima_actividad_fecha
  if (tieneActividad) return 'border-success/35 bg-success-light/15 hover:border-success/60'
  return 'border-warning/35 bg-warning-light/15 hover:border-warning/65'
}

function unitDotClass(unidad) {
  const tieneActividad = (unidad.resumen?.total_registros || 0) > 0 || unidad.resumen?.ultima_actividad_fecha
  if (tieneActividad) return 'bg-success'
  return 'bg-warning'
}

function unitStatusText(unidad) {
  const tieneActividad = (unidad.resumen?.total_registros || 0) > 0 || unidad.resumen?.ultima_actividad_fecha
  if (!tieneActividad) return 'Sin actividad registrada'
  if (unidad.resumen?.ultima_actividad_fecha) {
    return `Última: ${formatFecha(unidad.resumen.ultima_actividad_fecha)}`
  }
  return `${fmt(unidad.resumen.total_registros)} registro${unidad.resumen.total_registros !== 1 ? 's' : ''} en el periodo`
}

function compareUnitsByLastActivity(a, b) {
  const aDate = a.resumen?.ultima_actividad_fecha || ''
  const bDate = b.resumen?.ultima_actividad_fecha || ''
  if (aDate && bDate && aDate !== bDate) return String(bDate).localeCompare(String(aDate))
  if (aDate && !bDate) return -1
  if (!aDate && bDate) return 1
  return String(a.prefijo || a.nombre || '').localeCompare(String(b.prefijo || b.nombre || ''))
}

async function loadTodaySummary() {
  recordsStore.filtros.fecha_desde = selectedDateRange.value.from
  recordsStore.filtros.fecha_hasta = selectedDateRange.value.to
  await recordsStore.fetchMisRegistros()
}

async function loadAdminSummary() {
  const { from, to } = selectedDateRange.value
  await Promise.all([
    adminStore.fetchDashboard({ fecha_desde: from, fecha_hasta: to }),
    adminStore.fetchRecentRecords({ limit: 5 }),
  ])
}

async function reloadSummary() {
  await Promise.all([
    loadTodaySummary(),
    isAdmin.value ? loadAdminSummary() : Promise.resolve(),
  ])
}

function selectDatePreset(preset) {
  selectedDatePreset.value = preset
  if (preset === 'today') selectedDate.value = formatDateInput(new Date())
  reloadSummary()
}

function selectCustomDate() {
  selectedDatePreset.value = 'custom'
  reloadSummary()
}

function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

function addDays(date, days) {
  const next = new Date(date)
  next.setDate(next.getDate() + days)
  return next
}

function formatDateInput(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function formatDisplayDate(value) {
  const [y, m, d] = String(value).split('-').map(Number)
  if (!y || !m || !d) return value
  return new Intl.DateTimeFormat('es-AR', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
  }).format(new Date(y, m - 1, d))
}

function updateOnline() {
  isOnline.value = navigator.onLine
}

onMounted(async () => {
  await Promise.all([
    produccionStore.refreshPendingCount(),
    reloadSummary(),
  ])
  window.addEventListener('online', updateOnline)
  window.addEventListener('offline', updateOnline)
})

onUnmounted(() => {
  window.removeEventListener('online', updateOnline)
  window.removeEventListener('offline', updateOnline)
})
</script>
