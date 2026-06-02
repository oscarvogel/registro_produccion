<template>
  <div class="min-h-[calc(100vh-8.5rem)] bg-neutral-100 px-4 py-5 pb-24 md:min-h-[calc(100vh-3.5rem)] md:px-6 md:py-6">
    <div class="mx-auto w-full max-w-7xl space-y-5">
      <template v-if="isAdmin">
        <section class="rounded-2xl border border-primary-dark/20 bg-primary-dark p-5 text-white shadow-[0_18px_45px_rgba(20,61,35,0.20)] md:p-6">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <div class="mb-4 flex flex-wrap items-center gap-2">
                <span :class="['inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide', isOnline ? 'bg-success-light text-success-dark' : 'bg-warning-light text-warning-dark']">
                  <span :class="['h-2 w-2 rounded-full', isOnline ? 'bg-success' : 'bg-warning']"></span>
                  {{ isOnline ? 'En linea' : 'Sin conexion' }}
                </span>
                <span class="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-white/75">Administrador</span>
              </div>
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-white/60">{{ todayLabel }}</p>
              <h1 class="mt-2 text-3xl font-extrabold leading-tight md:text-5xl">Panel operativo general</h1>
              <p class="mt-2 max-w-2xl text-sm text-white/65">Estado general de produccion, unidades de negocio y sincronizacion del sistema.</p>
            </div>

            <button
              @click="$router.push({ name: 'produccion' })"
              class="inline-flex w-full items-center justify-between gap-4 rounded-xl bg-white px-4 py-3 text-left text-primary-dark shadow-lg transition-transform active:scale-[0.99] md:w-72"
              type="button"
            >
              <span>
                <span class="block text-xs font-bold uppercase tracking-[0.14em] text-primary/70">Accion rapida</span>
                <span class="mt-0.5 block text-lg font-extrabold">Cargar produccion</span>
              </span>
              <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-dark text-white">
                <AppIcon name="play" class="fill-current" />
              </span>
            </button>
          </div>

          <div class="mt-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
            <div v-for="card in adminSummaryCards" :key="card.label" class="rounded-xl border border-white/10 bg-white/8 p-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-white/55">{{ card.label }}</p>
              <div class="mt-2 flex items-baseline gap-1.5">
                <span class="text-2xl font-extrabold md:text-3xl">{{ adminStore.loading ? '-' : card.value }}</span>
                <span v-if="card.unit" class="text-xs font-semibold text-white/55">{{ card.unit }}</span>
              </div>
              <p class="mt-1 truncate text-xs text-white/50">{{ card.detail }}</p>
            </div>
          </div>
        </section>

        <section class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div class="space-y-5">
            <article class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
              <div class="mb-4 flex items-center justify-between gap-3">
                <div>
                  <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Estado por unidad de negocio</p>
                  <h2 class="mt-1 text-lg font-extrabold text-neutral-900">Actividad del dia</h2>
                </div>
                <AppIcon name="unit" size="lg" class="text-primary" />
              </div>

              <div v-if="adminStore.loading" class="space-y-2">
                <div v-for="i in 4" :key="i" class="h-12 animate-pulse rounded-xl bg-neutral-100"></div>
              </div>

              <div v-else class="divide-y divide-neutral-100">
                <div
                  v-for="unidad in pagedAdminUnits"
                  :key="unidad.id"
                  class="grid gap-3 py-3 sm:grid-cols-[5rem_minmax(0,1fr)_auto] sm:items-center"
                >
                  <span :class="['w-fit rounded-lg px-2.5 py-1 text-xs font-extrabold', unitStatusClass(unidad)]">
                    {{ unidad.prefijo || 'SIN' }}
                  </span>
                  <div class="min-w-0">
                    <p class="truncate text-sm font-bold text-neutral-800">{{ unidad.nombre }}</p>
                    <p class="text-xs text-neutral-400">{{ unitStatusText(unidad) }}</p>
                  </div>
                  <button
                    @click="$router.push({ name: 'admin-dashboard' })"
                    class="w-fit rounded-lg border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-600 hover:border-primary/40 hover:text-primary-dark"
                    type="button"
                  >
                    Ver detalle
                  </button>
                </div>
              </div>

              <div v-if="adminUnits.length > 0" class="mt-4 flex flex-col gap-3 border-t border-neutral-100 pt-4 sm:flex-row sm:items-center sm:justify-between">
                <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
                  <p class="text-xs font-semibold text-neutral-400">
                    Mostrando {{ adminUnitPageStart + 1 }}-{{ adminUnitPageEnd }} de {{ adminUnits.length }} unidades
                  </p>
                  <label class="flex items-center gap-2 text-xs font-semibold text-neutral-500">
                    Ver
                    <select
                      v-model.number="adminUnitsPerPage"
                      class="rounded-lg border border-neutral-200 bg-white px-2 py-1.5 text-xs font-bold text-neutral-700 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20"
                    >
                      <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
                    </select>
                    por pagina
                  </label>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="adminUnitPage = Math.max(1, adminUnitPage - 1)"
                    :disabled="adminUnitPage === 1"
                    class="rounded-lg border border-neutral-200 px-3 py-2 text-xs font-bold text-neutral-600 disabled:opacity-40"
                    type="button"
                  >
                    Anterior
                  </button>
                  <span class="rounded-lg bg-neutral-100 px-3 py-2 text-xs font-extrabold text-neutral-700">
                    {{ adminUnitPage }} / {{ adminUnitTotalPages }}
                  </span>
                  <button
                    @click="adminUnitPage = Math.min(adminUnitTotalPages, adminUnitPage + 1)"
                    :disabled="adminUnitPage === adminUnitTotalPages"
                    class="rounded-lg border border-neutral-200 px-3 py-2 text-xs font-bold text-neutral-600 disabled:opacity-40"
                    type="button"
                  >
                    Siguiente
                  </button>
                </div>
              </div>
            </article>

            <article class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
              <div class="mb-4 flex items-center justify-between gap-3">
                <div>
                  <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Ultimos registros del sistema</p>
                  <h2 class="mt-1 text-lg font-extrabold text-neutral-900">Cargas de hoy</h2>
                </div>
                <AppIcon name="records" size="lg" class="text-primary" />
              </div>

              <div v-if="adminStore.loadingRecentRecords" class="space-y-2">
                <div v-for="i in 3" :key="i" class="h-12 animate-pulse rounded-xl bg-neutral-100"></div>
              </div>

              <div v-else-if="adminStore.recentRecords.length > 0" class="divide-y divide-neutral-100">
                <div v-for="record in adminStore.recentRecords" :key="record.id" class="grid gap-2 py-3 md:grid-cols-[minmax(0,1fr)_8rem] md:items-center">
                  <div class="min-w-0">
                    <p class="truncate text-sm font-bold text-neutral-800">{{ record.operacion || 'Produccion' }} - {{ record.unidad || 'Sin unidad' }}</p>
                    <p class="truncate text-xs text-neutral-400">{{ record.operador || 'Sin operador' }} - {{ record.equipo || 'Sin equipo' }}</p>
                  </div>
                  <p class="text-sm font-extrabold text-primary-dark md:text-right">{{ fmt(record.produccion) }}</p>
                </div>
              </div>

              <div v-else class="rounded-xl border border-dashed border-neutral-300 bg-neutral-50 p-5 text-center">
                <p class="font-bold text-neutral-700">Sin registros cargados hoy</p>
                <p class="mt-1 text-sm text-neutral-500">Cuando se cargue produccion, los ultimos movimientos apareceran aca.</p>
              </div>
            </article>
          </div>

          <aside class="space-y-5">
            <article class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
              <div class="mb-4 flex items-center justify-between gap-3">
                <div>
                  <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Alertas operativas</p>
                  <h2 class="mt-1 text-lg font-extrabold text-neutral-900">{{ adminAlerts.length }} alerta{{ adminAlerts.length !== 1 ? 's' : '' }}</h2>
                </div>
                <AppIcon name="warning" size="lg" class="text-warning-dark" />
              </div>
              <div class="space-y-2">
                <p v-for="alert in adminAlerts" :key="alert" class="rounded-xl bg-warning-light/50 px-3 py-2 text-sm font-medium text-warning-dark">
                  {{ alert }}
                </p>
              </div>
            </article>

            <article class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Mi actividad</p>
              <h2 class="mt-1 text-lg font-extrabold text-neutral-900">{{ fmt(recordsStore.totales.total) }} registros cargados por mi hoy</h2>
              <p class="mt-1 text-sm text-neutral-500">Se mantiene como referencia personal, sin ocupar el foco del panel.</p>
            </article>

            <QuickActions
              :actions="adminActions"
              :show-install="Boolean(pwaInstall?.deferredInstallPrompt?.value)"
              @install="pwaInstall?.installApp"
            />
          </aside>
        </section>
      </template>

      <template v-else>
        <section class="grid gap-5 lg:grid-cols-[minmax(0,1.35fr)_minmax(22rem,0.65fr)]">
          <div class="rounded-2xl border border-primary-dark/20 bg-primary-dark p-5 text-white shadow-[0_18px_45px_rgba(20,61,35,0.20)] md:p-6">
            <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div class="min-w-0">
                <div class="mb-4 flex flex-wrap items-center gap-2">
                  <span :class="['inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide', isOnline ? 'bg-success-light text-success-dark' : 'bg-warning-light text-warning-dark']">
                    <span :class="['h-2 w-2 rounded-full', isOnline ? 'bg-success' : 'bg-warning']"></span>
                    {{ isOnline ? 'En linea' : 'Sin conexion' }}
                  </span>
                  <span class="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-white/75">{{ roleLabel }}</span>
                </div>
                <p class="text-sm font-semibold uppercase tracking-[0.16em] text-white/60">{{ todayLabel }}</p>
                <h1 class="mt-2 break-words text-3xl font-extrabold leading-tight md:text-5xl">{{ authStore.userName }}</h1>
              </div>

              <button
                @click="$router.push({ name: 'produccion' })"
                class="inline-flex w-full items-center justify-between gap-4 rounded-xl bg-white px-4 py-3 text-left text-primary-dark shadow-lg transition-transform active:scale-[0.99] md:w-72"
                type="button"
              >
                <span>
                  <span class="block text-xs font-bold uppercase tracking-[0.14em] text-primary/70">Iniciar tarea</span>
                  <span class="mt-0.5 block text-lg font-extrabold">Carga de Produccion</span>
                </span>
                <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-dark text-white">
                  <AppIcon name="play" class="fill-current" />
                </span>
              </button>
            </div>

            <div class="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
              <div v-for="card in operatorSummaryCards" :key="card.label" class="rounded-xl border border-white/10 bg-white/8 p-4">
                <p class="text-xs font-semibold uppercase tracking-wide text-white/55">{{ card.label }}</p>
                <div class="mt-2 flex items-baseline gap-1.5">
                  <span class="text-2xl font-extrabold md:text-3xl">{{ recordsStore.loading ? '-' : card.value }}</span>
                  <span v-if="card.unit" class="text-xs font-semibold text-white/55">{{ card.unit }}</span>
                </div>
                <p class="mt-1 truncate text-xs text-white/50">{{ card.detail }}</p>
              </div>
            </div>
          </div>

          <div class="grid gap-5">
            <LastPersonalRecord />
            <SyncCard />
          </div>
        </section>

        <section class="grid gap-5 lg:grid-cols-[minmax(0,1fr)_24rem]">
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <article v-for="metric in operatorCards" :key="metric.label" class="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
              <div class="mb-3 flex items-center justify-between gap-3">
                <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">{{ metric.label }}</p>
                <AppIcon :name="metric.icon" class="text-primary" />
              </div>
              <div class="flex items-baseline gap-1.5">
                <span class="text-3xl font-extrabold text-neutral-900">{{ recordsStore.loading ? '-' : metric.value }}</span>
                <span v-if="metric.unit" class="text-sm font-semibold text-neutral-400">{{ metric.unit }}</span>
              </div>
              <p class="mt-1 text-xs text-neutral-400">{{ metric.detail }}</p>
            </article>
          </div>

          <QuickActions
            :actions="operatorActions"
            :show-install="Boolean(pwaInstall?.deferredInstallPrompt?.value)"
            @install="pwaInstall?.installApp"
          />
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
const adminUnitPage = ref(1)
const adminUnitsPerPage = ref(5)
const pageSizeOptions = [5, 10, 25, 50]

const isAdmin = computed(() => authStore.isAdmin)

const todayIso = computed(() => {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
})

const todayLabel = computed(() => {
  return new Intl.DateTimeFormat('es-AR', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
  }).format(new Date())
})

const roleLabel = computed(() => {
  if (authStore.user?.encargado === 1) return 'Encargado'
  return 'Operador'
})

const adminTotals = computed(() => {
  return adminStore.dashboard.reduce((acc, unidad) => {
    const resumen = unidad.resumen || {}
    acc.registros += Number(resumen.total_registros || 0)
    acc.produccion += Number(resumen.produccion_total || 0)
    acc.combustible += Number(resumen.combustible_total || 0)
    acc.operadores += Number(resumen.operadores_activos || 0)
    if (Number(resumen.total_registros || 0) > 0) acc.unidadesActivas += 1
    return acc
  }, { registros: 0, produccion: 0, combustible: 0, operadores: 0, unidadesActivas: 0 })
})

const adminUnits = computed(() => [...adminStore.dashboard].sort((a, b) => String(a.prefijo || a.nombre).localeCompare(String(b.prefijo || b.nombre))))
const inactiveUnits = computed(() => adminUnits.value.filter((unidad) => Number(unidad.resumen?.total_registros || 0) === 0))
const adminUnitTotalPages = computed(() => Math.max(1, Math.ceil(adminUnits.value.length / adminUnitsPerPage.value)))
const adminUnitPageStart = computed(() => (adminUnitPage.value - 1) * adminUnitsPerPage.value)
const adminUnitPageEnd = computed(() => Math.min(adminUnitPageStart.value + adminUnitsPerPage.value, adminUnits.value.length))
const pagedAdminUnits = computed(() => adminUnits.value.slice(adminUnitPageStart.value, adminUnitPageEnd.value))

watch(adminUnitTotalPages, (totalPages) => {
  if (adminUnitPage.value > totalPages) {
    adminUnitPage.value = totalPages
  }
})

watch(adminUnitsPerPage, () => {
  adminUnitPage.value = 1
})

const adminSummaryCards = computed(() => [
  {
    label: 'Produccion total hoy',
    value: fmt(adminTotals.value.produccion),
    unit: '',
    detail: 'Todas las unidades',
  },
  {
    label: 'Registros hoy',
    value: fmt(adminTotals.value.registros),
    unit: '',
    detail: 'Cargas del sistema',
  },
  {
    label: 'Unidades activas',
    value: `${adminTotals.value.unidadesActivas} / ${adminUnits.value.length}`,
    unit: '',
    detail: inactiveUnits.value.length ? `${inactiveUnits.value.length} sin actividad` : 'Todas con actividad',
  },
  {
    label: 'Pendientes offline',
    value: fmt(produccionStore.pendingCount),
    unit: '',
    detail: syncText.value,
  },
])

const adminAlerts = computed(() => {
  const alerts = []
  if (!isOnline.value) alerts.push('Sistema sin conexion: las cargas quedan en cola local.')
  if (produccionStore.pendingCount > 0) alerts.push(`${produccionStore.pendingCount} registro(s) pendientes de sincronizacion.`)
  if (inactiveUnits.value.length > 0) {
    const names = inactiveUnits.value.slice(0, 4).map((unidad) => unidad.prefijo || unidad.nombre).join(', ')
    alerts.push(`Unidades sin actividad hoy: ${names}${inactiveUnits.value.length > 4 ? '...' : ''}.`)
  }
  if (alerts.length === 0) alerts.push('Sin alertas operativas para hoy.')
  return alerts
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
  return options.find((item) => Number(item.value) > 0) || { label: 'Produccion', value: 0, unit: '' }
})

const sortedRecords = computed(() => {
  return [...recordsStore.registros].sort((a, b) => {
    const dateDiff = String(b.fecha || '').localeCompare(String(a.fecha || ''))
    if (dateDiff !== 0) return dateDiff
    return Number(b.id || 0) - Number(a.id || 0)
  })
})

const lastRecord = computed(() => sortedRecords.value[0] || null)
const lastRecordTitle = computed(() => lastRecord.value?.operacion || 'Sin actividad hoy')

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

const operatorSummaryCards = computed(() => [
  { label: 'Produccion hoy', value: fmt(productionToday.value.value), unit: productionToday.value.unit, detail: productionToday.value.label },
  { label: 'Horas', value: fmt(recordsStore.totales.total_horas), unit: 'hs', detail: 'Tiempo trabajado' },
  { label: 'Registros', value: fmt(recordsStore.totales.total), unit: '', detail: 'Cargas del dia' },
  { label: 'Combustible', value: fmt(recordsStore.totales.total_combustible), unit: 'lts', detail: 'Consumo cargado' },
])

const operatorCards = computed(() => [
  {
    label: 'Tiempo trabajado',
    value: fmt(recordsStore.totales.total_horas),
    unit: 'hs',
    detail: `${fmt(recordsStore.totales.total)} registro${Number(recordsStore.totales.total) !== 1 ? 's' : ''} hoy`,
    icon: 'timer',
  },
  {
    label: 'Combustible',
    value: fmt(recordsStore.totales.total_combustible),
    unit: 'lts',
    detail: recordsStore.totales.combustible_por_hora != null ? `${fmt(recordsStore.totales.combustible_por_hora)} lts/hs` : 'Sin promedio disponible',
    icon: 'fuel',
  },
  {
    label: 'Pendientes',
    value: fmt(produccionStore.pendingCount),
    unit: '',
    detail: isOnline.value ? 'Listo para sincronizar' : 'Se enviaran al reconectar',
    icon: 'offline',
  },
  {
    label: 'Ultima carga',
    value: lastRecord.value ? horaRegistro(lastRecord.value) : '-',
    unit: '',
    detail: lastRecord.value?.equipo || 'Sin registros hoy',
    icon: 'timer',
  },
])

const operatorActions = computed(() => {
  const list = [
    { name: 'pendientes', label: 'Registros pendientes', description: 'Cola offline y reintentos.', to: { name: 'pendientes' }, badge: produccionStore.pendingCount },
  ]
  if (authStore.user?.encargado === 1) {
    list.push({ name: 'dashboard', label: 'Dashboard', description: 'Resumen por unidad y proceso.', to: { name: 'dashboard' }, badge: null })
  } else {
    list.push({ name: 'mis-registros', label: 'Mis Registros', description: 'Historial y totales personales.', to: { name: 'mis-registros' }, badge: null })
  }
  return list
})

const adminActions = computed(() => [
  { name: 'produccion', label: 'Cargar produccion', description: 'Registrar una carga manual.', to: { name: 'produccion' }, badge: null },
  { name: 'pendientes', label: 'Ver pendientes', description: 'Cola offline y reintentos.', to: { name: 'pendientes' }, badge: produccionStore.pendingCount },
  { name: 'admin', label: 'Panel admin', description: 'Catalogos, permisos y relaciones.', to: { name: 'admin-dashboard' }, badge: null },
  { name: 'mis-registros', label: 'Mis registros', description: 'Actividad cargada por mi usuario.', to: { name: 'mis-registros' }, badge: null },
])

const syncText = computed(() => {
  if (!isOnline.value) return 'Sin conexion'
  if (produccionStore.syncingPending) return 'Sincronizando'
  if (produccionStore.pendingCount > 0) return 'Con pendientes'
  return 'Todo sincronizado'
})

const QuickActions = defineComponent({
  props: {
    actions: { type: Array, required: true },
    showInstall: { type: Boolean, default: false },
  },
  emits: ['install'],
  setup(props, { emit }) {
    return () => h('article', { class: 'rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm' }, [
      h('div', { class: 'mb-4' }, [
        h('p', { class: 'text-xs font-bold uppercase tracking-wide text-neutral-400' }, 'Accesos rapidos'),
        h('h2', { class: 'mt-1 text-lg font-extrabold text-neutral-900' }, 'Operaciones'),
      ]),
      h('div', { class: 'grid gap-2' }, [
        ...props.actions.map((action) => h('button', {
          key: action.name,
          type: 'button',
          class: 'flex w-full items-center justify-between gap-3 rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-3 text-left transition-colors hover:border-primary/40 hover:bg-white',
          onClick: () => router.push(action.to),
        }, [
          h('span', { class: 'min-w-0' }, [
            h('span', { class: 'block truncate text-sm font-extrabold text-neutral-800' }, action.label),
            h('span', { class: 'block truncate text-xs text-neutral-400' }, action.description),
          ]),
          action.badge !== null ? h('span', { class: 'rounded-lg bg-warning-light px-2.5 py-1 text-xs font-extrabold text-warning-dark' }, String(action.badge)) : null,
        ])),
        props.showInstall ? h('button', {
          type: 'button',
          class: 'flex w-full items-center justify-between gap-3 rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-3 text-left transition-colors hover:border-primary/40 hover:bg-white',
          onClick: () => emit('install'),
        }, h('span', [
          h('span', { class: 'block text-sm font-extrabold text-neutral-800' }, 'Instalar app'),
          h('span', { class: 'block text-xs text-neutral-400' }, 'Acceso rapido y soporte offline.'),
        ])) : null,
      ]),
    ])
  },
})

const LastPersonalRecord = defineComponent({
  setup() {
    return () => h('article', { class: 'rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm' }, [
      h('div', { class: 'mb-4 flex items-center justify-between gap-3' }, [
        h('div', [
          h('p', { class: 'text-xs font-bold uppercase tracking-wide text-neutral-400' }, 'Ultimo registro'),
          h('h2', { class: 'mt-1 text-lg font-extrabold text-neutral-900' }, lastRecordTitle.value),
        ]),
        h(AppIcon, { name: 'records', size: 'lg', class: 'text-primary' }),
      ]),
      recordsStore.loading
        ? h('div', { class: 'space-y-2' }, [h('div', { class: 'h-4 w-2/3 animate-pulse rounded bg-neutral-200' }), h('div', { class: 'h-4 w-1/2 animate-pulse rounded bg-neutral-100' })])
        : lastRecord.value
          ? h('div', { class: 'space-y-3' }, [
            h('p', { class: 'text-sm text-neutral-500' }, `${formatFecha(lastRecord.value.fecha)} - ${lastRecord.value.equipo || 'Sin equipo'}`),
            h('div', { class: 'flex flex-wrap gap-2' }, lastRecordMetrics.value.map((metric) => h('span', { key: metric.label, class: 'rounded-lg bg-neutral-100 px-2.5 py-1 text-xs font-bold text-neutral-700' }, `${metric.value} ${metric.unit}`))),
          ])
          : h('p', { class: 'text-sm text-neutral-500' }, 'Todavia no hay registros cargados para hoy.'),
    ])
  },
})

const SyncCard = defineComponent({
  setup() {
    return () => h('article', { class: 'rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm' }, [
      h('div', { class: 'mb-4 flex items-center justify-between gap-3' }, [
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

function fmt(val) {
  const n = Number(val || 0)
  return n.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
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
  const registros = Number(unidad.resumen?.total_registros || 0)
  if (produccionStore.pendingCount > 0) return 'bg-error-light text-error-dark'
  if (registros > 0) return 'bg-success-light text-success-dark'
  return 'bg-warning-light text-warning-dark'
}

function unitStatusText(unidad) {
  const registros = Number(unidad.resumen?.total_registros || 0)
  if (registros > 0) return `${fmt(registros)} registro${registros !== 1 ? 's' : ''} hoy`
  return 'Sin actividad hoy'
}

async function loadTodaySummary() {
  recordsStore.filtros.fecha_desde = todayIso.value
  recordsStore.filtros.fecha_hasta = todayIso.value
  await recordsStore.fetchMisRegistros()
}

async function loadAdminSummary() {
  await Promise.all([
    adminStore.fetchDashboard({ fecha_desde: todayIso.value, fecha_hasta: todayIso.value }),
    adminStore.fetchRecentRecords({ fecha: todayIso.value, limit: 5 }),
  ])
}

function updateOnline() {
  isOnline.value = navigator.onLine
}

onMounted(async () => {
  await Promise.all([
    produccionStore.refreshPendingCount(),
    loadTodaySummary(),
    isAdmin.value ? loadAdminSummary() : Promise.resolve(),
  ])
  window.addEventListener('online', updateOnline)
  window.addEventListener('offline', updateOnline)
})

onUnmounted(() => {
  window.removeEventListener('online', updateOnline)
  window.removeEventListener('offline', updateOnline)
})
</script>
