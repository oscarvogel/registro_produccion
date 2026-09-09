<template>
  <div class="min-h-[calc(100vh-8.5rem)] bg-surface px-3 py-3 md:min-h-[calc(100vh-3.5rem)] md:px-4 md:py-4">
    <div class="content-default mx-auto space-y-3">
      <PageHeader
        title="Registros Pendientes"
        :description="scopeDescription"
      >
        <template #kicker>
          <AppBadge :tone="backendReachable ? 'success' : navigatorOnline ? 'error' : 'warning'">
            {{ backendReachable ? 'Servidor disponible' : navigatorOnline ? 'Servidor no disponible' : 'Sin conexión' }}
          </AppBadge>
          <AppBadge v-if="scopedFailedRecords.length > 0" tone="error">
            {{ scopedFailedRecords.length }} fallido{{ scopedFailedRecords.length !== 1 ? 's' : '' }}
          </AppBadge>
        </template>
        <template #actions>
          <AppButton variant="secondary" @click="loadRecords">
            <AppIcon name="refresh" size="sm" />
            Refrescar
          </AppButton>
          <AppButton :loading="syncing" :disabled="!backendReachable || scopedPendingRecords.length === 0" @click="syncAll">
            <AppIcon name="sync" size="sm" />
            Sincronizar
          </AppButton>
        </template>
      </PageHeader>

      <section class="app-card rounded-xl p-3.5">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-xs font-extrabold uppercase tracking-wide text-on-surface-variant">Estado de sincronización</p>
            <h2 class="mt-1 text-xl font-extrabold text-neutral-950">{{ syncStatusTitle }}</h2>
            <p class="mt-1 text-sm text-on-surface-variant">
              {{ backendReachable ? 'Servidor disponible' : navigatorOnline ? 'Wi-Fi conectado, servidor inaccesible' : 'Sistema sin conexión' }} · {{ healthMessage }} · Última revisión: {{ lastCheckLabel }}
            </p>
          </div>
          <div class="flex h-12 w-12 items-center justify-center rounded-full bg-info-light text-info-dark">
            <AppIcon :name="isHealthy ? 'success' : 'warning'" size="lg" />
          </div>
        </div>
      </section>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Pendientes locales"
          :value="localPendingRecords.length"
          description="Registros esperando sincronización"
          icon="pending"
          tone="warning"
        />
        <MetricCard
          label="Fallidos locales"
          :value="localFailedRecords.length"
          description="Registros con error al enviar"
          icon="warning"
          tone="error"
        />
        <MetricCard
          :label="systemPendingLabel"
          :value="scopedPendingRecords.length"
          :description="systemPendingDescription"
          icon="sync"
          tone="primary"
        />
        <MetricCard
          :label="systemFailedLabel"
          :value="scopedFailedRecords.length"
          :description="systemFailedDescription"
          icon="records"
          tone="neutral"
        />
      </div>

      <section class="app-card rounded-xl p-3.5">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-xs font-extrabold uppercase tracking-wide text-on-surface-variant">Cola de sincronización</p>
            <h2 class="mt-1 text-lg font-extrabold text-on-surface">{{ queueTitle }}</h2>
          </div>

          <div v-if="scopedRecords.length > 0" class="flex flex-wrap gap-2">
            <button
              v-for="filter in filters"
              :key="filter.value"
              type="button"
              :class="[
                'rounded-full border px-3 py-1.5 text-xs font-bold transition-colors',
                activeFilter === filter.value
                  ? 'border-secondary bg-secondary text-on-secondary'
                  : 'app-button-soft border',
              ]"
              @click="activeFilter = filter.value"
            >
              {{ filter.label }}
            </button>
          </div>
        </div>

        <div v-if="loading" class="mt-3 rounded-lg border border-outline-variant bg-surface-container-low p-4 text-center text-sm text-on-surface-variant">
          Cargando registros...
        </div>

        <div v-else-if="visibleRecords.length === 0" class="mt-3">
          <EmptyState
            :title="emptyStateTitle"
            :description="emptyStateDescription"
            icon="sync"
          >
            <p class="mt-3 text-xs font-semibold text-outline">Última verificación: {{ lastCheckFullLabel }}</p>
          </EmptyState>
        </div>

        <div v-else class="mt-3 space-y-2.5">
          <article
            v-for="record in visibleRecords"
            :key="record.id"
            :class="[
              'rounded-xl border p-3.5 shadow-sm',
              isFailedRecord(record) ? 'border-error/30 bg-error-light/20' : 'border-warning/30 bg-warning-light/20',
            ]"
          >
            <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <AppBadge :tone="isFailedRecord(record) ? 'error' : 'warning'">
                    {{ isFailedRecord(record) ? 'Falló sincronización' : 'Pendiente' }}
                  </AppBadge>
                  <span class="text-xs text-outline">{{ formatDate(record.timestamp) }}</span>
                </div>
                <p class="mt-2 text-base font-extrabold text-on-surface">
                  Producción - {{ record.payload?.UN || 'Unidad sin definir' }}
                </p>
                <dl class="mt-2 grid gap-1 text-sm text-on-surface-variant sm:grid-cols-2 xl:grid-cols-4">
                  <div><dt class="inline font-bold text-on-surface">Fecha:</dt> <dd class="inline">{{ record.payload?.fecha || '-' }}</dd></div>
                  <div><dt class="inline font-bold text-on-surface">Proceso:</dt> <dd class="inline">{{ record.payload?.operacion || '-' }}</dd></div>
                  <div><dt class="inline font-bold text-on-surface">Operador:</dt> <dd class="inline">{{ record.payload?.operador || 'Sin definir' }}</dd></div>
                  <div><dt class="inline font-bold text-on-surface">Equipo:</dt> <dd class="inline">{{ record.payload?.equipo || 'Sin definir' }}</dd></div>
                </dl>
                <p v-if="record.syncError" class="mt-3 rounded-lg bg-error-light px-3 py-2 text-sm font-semibold text-error-dark">
                  Error: {{ record.syncError }}
                </p>
              </div>

              <div class="flex flex-wrap gap-2 md:justify-end">
                <AppButton
                  variant="primary"
                  size="sm"
                  :disabled="!navigatorOnline || retryingId === record.id"
                  :loading="retryingId === record.id"
                  @click="retryRecord(record)"
                >
                  <AppIcon name="retry" size="sm" />
                  Reintentar
                </AppButton>
                <AppButton variant="secondary" size="sm" @click="openDetail(record)">
                  <AppIcon name="edit" size="sm" />
                  Ver detalle
                </AppButton>
                <AppButton variant="danger" size="sm" @click="discardRecord(record)">
                  <AppIcon name="delete" size="sm" />
                  Eliminar
                </AppButton>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="app-card rounded-xl p-3.5">
        <div class="flex items-start gap-3">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-surface-container text-info-dark">
            <AppIcon name="refresh" />
          </div>
          <div>
            <p class="text-xs font-extrabold uppercase tracking-wide text-on-surface-variant">Actividad reciente</p>
            <p class="mt-1 text-sm font-semibold text-on-surface">{{ recentActivityTitle }}</p>
            <p class="mt-1 text-sm text-on-surface-variant">{{ recentActivityDescription }}</p>
          </div>
        </div>
      </section>

      <AppModal
        v-model="showDetail"
        title="Detalle del registro pendiente"
        description="Información del registro guardado en este teléfono."
      >
        <div v-if="selectedRecord" class="space-y-3" data-testid="pending-record-detail">
          <div class="app-surface-muted flex flex-col gap-3 rounded-lg border p-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-xs font-extrabold uppercase tracking-wide text-on-surface-variant">{{ selectedRecord.payload?.operacion || 'Registro de producción' }}</p>
              <p class="mt-1 text-lg font-extrabold text-on-surface">{{ selectedRecord.payload?.UN || 'Unidad sin definir' }}</p>
              <p class="mt-1 text-xs font-semibold text-on-surface-variant">Guardado {{ formatDate(selectedRecord.timestamp) }}</p>
            </div>
            <AppBadge :tone="isFailedRecord(selectedRecord) ? 'error' : 'warning'">
              {{ synchronizationStatusLabel(selectedRecord) }}
            </AppBadge>
          </div>

          <section
            v-for="grupo in selectedRecordGroups"
            :key="grupo.title"
            class="rounded-lg border border-outline-variant p-3"
          >
            <h4 class="mb-2 text-xs font-extrabold uppercase tracking-wide text-on-surface-variant">{{ grupo.title }}</h4>
            <dl class="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
              <div v-for="field in grupo.fields" :key="field.key" class="min-w-0">
                <dt class="text-[11px] font-semibold uppercase tracking-wide text-outline">{{ field.label }}</dt>
                <dd class="mt-0.5 break-words text-sm font-semibold text-on-surface">{{ formatDetailValue(field.value, field.type) }}</dd>
              </div>
            </dl>
          </section>

          <button
            type="button"
            class="app-button-soft inline-flex items-center rounded-lg border px-3 py-2 text-xs font-bold"
            @click="showTechnicalData = !showTechnicalData"
          >
            {{ showTechnicalData ? 'Ocultar datos técnicos' : 'Ver datos técnicos' }}
          </button>

          <pre
            v-if="showTechnicalData"
            class="max-h-[45vh] overflow-auto rounded-lg bg-neutral-900 p-4 text-xs text-white"
            data-testid="pending-record-technical-data"
          >{{ selectedRecordText }}</pre>
        </div>
      </AppModal>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import api from '@/services/api'
import { ensurePendingIdentity } from '@/services/pendingRecords'
import db from '@/services/db'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import { useConnectivityStore } from '@/stores/connectivity'
import { useToastStore } from '@/stores/toast'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import AppModal from '@/components/ui/AppModal.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import PageHeader from '@/components/ui/PageHeader.vue'

const authStore = useAuthStore()
const produccionStore = useProduccionStore()
const connectivityStore = useConnectivityStore()
const toast = useToastStore()

const records = ref([])
const loading = ref(false)
const syncing = ref(false)
const retryingId = ref(null)
const showDetail = ref(false)
const showTechnicalData = ref(false)
const selectedRecord = ref(null)
const navigatorOnline = ref(navigator.onLine)
const backendReachable = computed(() => navigatorOnline.value && connectivityStore.isBackendUp)
const lastCheckAt = ref(null)
const activeFilter = ref('all')

const isAdmin = computed(() => authStore.isAdmin)
const isEncargado = computed(() => authStore.user?.encargado === 1)
const currentUserId = computed(() => Number(authStore.user?.idPersonal || 0))
const userUnitIds = computed(() => {
  const ids = Array.isArray(authStore.user?.unidad_ids) ? authStore.user.unidad_ids : []
  const mainUnit = authStore.user?.unidad_negocio
  return new Set([...ids, mainUnit].map((value) => Number(value)).filter(Boolean))
})

const scopedRecords = computed(() => {
  if (isAdmin.value) return records.value
  if (isEncargado.value) {
    return records.value.filter((record) => userUnitIds.value.has(Number(record.payload?.cod_un || 0)))
  }
  return records.value.filter((record) => Number(record.payload?.cod_operador || 0) === currentUserId.value)
})

const localPendingRecords = computed(() => records.value.filter(isPendingRecord))
const localFailedRecords = computed(() => records.value.filter(isFailedRecord))
const scopedPendingRecords = computed(() => scopedRecords.value.filter(isPendingRecord))
const scopedFailedRecords = computed(() => scopedRecords.value.filter(isFailedRecord))
const selectedRecordText = computed(() => JSON.stringify(selectedRecord.value?.payload || {}, null, 2))
const selectedRecordGroups = computed(() => {
  const payload = selectedRecord.value?.payload || {}
  const groups = [
    {
      title: 'Identificación',
      fields: [
        detailField('fecha', 'Fecha', payload.fecha, 'date'),
        detailField('UN', 'Unidad de negocio', payload.UN),
        detailField('operador', 'Operador', payload.operador),
        detailField('equipo', 'Equipo / máquina', payload.equipo),
        detailField('operacion', 'Proceso / actividad', payload.operacion),
      ],
    },
    {
      title: 'Tiempos y operación',
      fields: [
        detailField('hr_inicio', 'Horómetro inicial', payload.hr_inicio, 'number'),
        detailField('hr_fin', 'Horómetro final', payload.hr_fin, 'number'),
        detailField('km_combustible', 'Horómetro / km de combustible', payload.km_combustible, 'number'),
        detailField('hr_disposicion', 'Horas de disposición', payload.hr_disposicion, 'number'),
        detailField('hrs_no_op', 'Horas no operativas', payload.hrs_no_op, 'number'),
        detailField('motivo_no_op', 'Motivo no operativo', payload.motivo_no_op),
      ],
    },
    {
      title: 'Producción',
      fields: [
        detailField('produccion', 'Producción', payload.produccion, 'number'),
        detailField('unidad_produccion', 'Unidad de producción', payload.unidad_produccion),
        detailField('tn_despachadas', 'Toneladas despachadas', payload.tn_despachadas, 'number'),
        detailField('m3', 'Metros cúbicos', payload.m3, 'number'),
        detailField('has', 'Hectáreas', payload.has, 'number'),
        detailField('carros', 'Carros', payload.carros, 'number'),
        detailField('plantas', 'Plantas', payload.plantas, 'number'),
        detailField('mtrs_recorridos', 'Metros recorridos', payload.mtrs_recorridos, 'number'),
        detailField('km_carreteo', 'Kilómetros de carreteo', payload.km_carreteo, 'number'),
        detailField('km_perfilado', 'Kilómetros de perfilado', payload.km_perfilado, 'number'),
        detailField('pulpable', 'Pulpable', payload.pulpable, 'number'),
        detailField('pies_16', 'Pies de 16', payload.pies_16, 'number'),
        detailField('pies_14', 'Pies de 14', payload.pies_14, 'number'),
        detailField('pies_12', 'Pies de 12', payload.pies_12, 'number'),
        detailField('pies_10', 'Pies de 10', payload.pies_10, 'number'),
      ],
    },
    {
      title: 'Consumos',
      fields: [
        detailField('combustible', 'Combustible', payload.combustible, 'number'),
        detailField('aceite_cadena', 'Aceite de cadena', payload.aceite_cadena, 'number'),
        detailField('aceite_hidraulico', 'Aceite hidráulico', payload.aceite_hidraulico, 'number'),
        detailField('aceite_motor', 'Aceite de motor', payload.aceite_motor, 'number'),
        detailField('aceite_embrague', 'Aceite de embrague', payload.aceite_embrague, 'number'),
        detailField('aceite_transmision', 'Aceite de transmisión', payload.aceite_transmision, 'number'),
      ],
    },
    {
      title: 'Ubicación y remitos',
      fields: [
        detailField('lugar_carga', 'Lugar de carga', payload.lugar_carga, 'number'),
        detailField('predio', 'Predio', payload.predio),
        detailField('acta', 'Acta', payload.acta),
        detailField('rodal', 'Rodal', payload.rodal),
        detailField('remito', 'Remito 1', payload.remito),
        detailField('remito2', 'Remito 2', payload.remito2),
        detailField('remito3', 'Remito 3', payload.remito3),
      ],
    },
    {
      title: 'Observaciones',
      fields: [detailField('observaciones', 'Observaciones', payload.observaciones)],
    },
    {
      title: 'Sincronización',
      fields: [
        detailField('sync-status', 'Estado', synchronizationStatusLabel(selectedRecord.value)),
        detailField('retry-count', 'Intentos realizados', selectedRecord.value?.retryCount, 'number'),
        detailField('sync-error', 'Mensaje de error', selectedRecord.value?.syncError),
      ],
    },
  ]

  return groups
    .map((group) => ({ ...group, fields: group.fields.filter((field) => hasDetailValue(field.value)) }))
    .filter((group) => group.fields.length > 0)
})

const filters = computed(() => [
  { value: 'all', label: `Todos (${scopedRecords.value.length})` },
  { value: 'pending', label: `Pendientes (${scopedPendingRecords.value.length})` },
  { value: 'failed', label: `Fallidos (${scopedFailedRecords.value.length})` },
])

const visibleRecords = computed(() => {
  if (activeFilter.value === 'pending') return scopedPendingRecords.value
  if (activeFilter.value === 'failed') return scopedFailedRecords.value
  return scopedRecords.value
})

const emptyStateTitle = computed(() => {
  if (scopedRecords.value.length > 0) return 'No hay registros en este filtro'
  return 'Todo sincronizado'
})

const emptyStateDescription = computed(() => {
  if (scopedRecords.value.length > 0) return 'Cambiá el filtro para ver los registros que todavía requieren atención.'
  return 'No hay registros pendientes ni fallidos en este teléfono.'
})

const scopeDescription = computed(() => {
  if (isAdmin.value) return 'Vista de la cola local de este dispositivo y su estado de sincronización.'
  if (isEncargado.value) return 'Vista de registros pendientes o fallidos para tus unidades de negocio asignadas.'
  return 'Vista de registros pendientes o fallidos generados por tu usuario.'
})

const systemPendingLabel = computed(() => {
  if (isAdmin.value) return 'Pendientes en este dispositivo'
  if (isEncargado.value) return 'Pendientes unidad'
  return 'Mis pendientes'
})

const systemFailedLabel = computed(() => {
  if (isAdmin.value) return 'Fallidos en este dispositivo'
  if (isEncargado.value) return 'Fallidos unidad'
  return 'Mis fallidos'
})

const systemPendingDescription = computed(() => {
  if (isAdmin.value) return 'Registros locales: esperando sincronización'
  if (isEncargado.value) return 'Registros de tus unidades asignadas'
  return 'Registros creados por tu usuario'
})

const systemFailedDescription = computed(() => {
  if (isAdmin.value) return 'Registros locales: con error de sincronización'
  if (isEncargado.value) return 'Errores dentro de tus unidades'
  return 'Errores de tus cargas locales'
})

const isHealthy = computed(() => backendReachable.value && scopedRecords.value.length === 0)
const syncStatusTitle = computed(() => {
  if (!navigatorOnline.value) return 'Sin conexión'
  if (!connectivityStore.isBackendUp) return 'Servidor no disponible'
  if (scopedFailedRecords.value.length > 0) return 'Requiere revisión'
  if (scopedPendingRecords.value.length > 0) return 'Con registros pendientes'
  return 'Todo sincronizado'
})

const healthMessage = computed(() => {
  if (!navigatorOnline.value) return 'Las nuevas cargas quedarán guardadas en este equipo'
  if (!connectivityStore.isBackendUp) return 'El Wi-Fi funciona, pero el servidor no responde'
  if (scopedFailedRecords.value.length > 0) return `${scopedFailedRecords.value.length} registro(s) fallidos`
  if (scopedPendingRecords.value.length > 0) return `${scopedPendingRecords.value.length} registro(s) esperando envío`
  return 'Sin conflictos detectados'
})

const queueTitle = computed(() => {
  if (loading.value) return 'Revisando cola offline'
  if (scopedRecords.value.length === 0) return 'Todo sincronizado'
  return `${scopedRecords.value.length} registro(s) requieren atención`
})

const recentActivityTitle = computed(() => {
  const transientAttempts = scopedPendingRecords.value.filter((record) => Number(record.retryCount || 0) > 0 || record.syncError)
  if (transientAttempts.length > 0) return `${transientAttempts.length} envío(s) intentado(s) sin confirmación.`
  if (scopedFailedRecords.value.length === 0) return 'No hubo intentos fallidos de sincronización.'
  return `${scopedFailedRecords.value.length} intento(s) fallidos detectados.`
})

const recentActivityDescription = computed(() => {
  const transientAttempts = scopedPendingRecords.value.filter((record) => Number(record.retryCount || 0) > 0 || record.syncError)
  if (transientAttempts.length > 0) {
    const lastAttempt = [...transientAttempts].sort((a, b) => Number(b.lastAttemptAt || b.timestamp || 0) - Number(a.lastAttemptAt || a.timestamp || 0))[0]
    return `Último intento sin confirmar: ${lastAttempt?.syncError || 'el servidor no respondió'}.`
  }
  if (scopedFailedRecords.value.length === 0) return 'La cola offline no registra errores para el alcance actual.'
  const lastFailed = [...scopedFailedRecords.value].sort((a, b) => Number(b.failedAt || b.timestamp || 0) - Number(a.failedAt || a.timestamp || 0))[0]
  return `Último error: ${lastFailed?.syncError || 'sin detalle disponible'}.`
})

const lastCheckLabel = computed(() => {
  if (!lastCheckAt.value) return 'sin revisar'
  const diff = Date.now() - lastCheckAt.value
  if (diff < 60000) return 'hace unos segundos'
  const minutes = Math.max(1, Math.round(diff / 60000))
  return `hace ${minutes} min`
})

const lastCheckFullLabel = computed(() => {
  if (!lastCheckAt.value) return '-'
  return formatDate(lastCheckAt.value)
})

onMounted(() => {
  loadRecords()
  window.addEventListener('online', updateOnline)
  window.addEventListener('offline', updateOnline)
})

onUnmounted(() => {
  window.removeEventListener('online', updateOnline)
  window.removeEventListener('offline', updateOnline)
})

function isFailedRecord(record) {
  return record?.synced === 1 || record?.syncStatus === 'failed'
}

function isPendingRecord(record) {
  return !isFailedRecord(record)
}

function updateOnline() {
  navigatorOnline.value = navigator.onLine
  lastCheckAt.value = Date.now()
}

async function loadRecords() {
  loading.value = true
  try {
    records.value = await db.pendingRecords.orderBy('timestamp').reverse().toArray()
    await produccionStore.refreshPendingCount()
    lastCheckAt.value = Date.now()
  } finally {
    loading.value = false
  }
}

async function syncAll() {
  syncing.value = true
  try {
    const result = await produccionStore.syncPending()
    await loadRecords()
    if (result.permanentFailureCount > 0) {
      toast.error(
        'Sincronización parcial',
        `${result.permanentFailureCount} registro(s) fueron rechazados por el servidor y requieren revisión.`,
      )
    } else if (result.pendingCount > 0) {
      toast.error(
        'Sincronización pendiente',
        `Se enviaron ${result.successCount} registro(s); ${result.pendingCount} siguen guardados solo en este teléfono.`,
      )
    } else {
      toast.success('Sincronización completa', `${result.successCount} registro(s) confirmados por el servidor.`)
    }
  } catch {
    toast.error('No se pudo sincronizar', 'Revisá la conexión o intentá de nuevo.')
  } finally {
    syncing.value = false
  }
}

async function retryRecord(record) {
  retryingId.value = record.id
  try {
    await db.pendingRecords.update(record.id, {
      syncStatus: 'syncing',
      lastAttemptAt: Date.now(),
      retryCount: Number(record.retryCount || 0) + 1,
    })
    const submissionPayload = await ensurePendingIdentity(record)
    await api.post('/api/produccion', submissionPayload, {
      _suppressErrorToast: true,
    })
    await db.pendingRecords.delete(record.id)
    await loadRecords()
    toast.success('Registro sincronizado')
  } catch (err) {
    const detail = err.response?.data?.detail || 'No se pudo sincronizar este registro.'
    const status = err.response?.status
    const permanent = status >= 400 && status < 500 && ![401, 403, 408, 429].includes(status)
    const update = {
      synced: permanent ? 1 : 0,
      syncStatus: permanent ? 'failed' : 'pending',
      syncError: [401, 403].includes(status)
        ? 'La sesión debe validarse nuevamente antes de enviar.'
        : detail,
    }
    if (permanent) update.failedAt = Date.now()
    await db.pendingRecords.update(record.id, update)
    await loadRecords()
    toast.error('Sincronización fallida', detail)
  } finally {
    retryingId.value = null
  }
}

async function discardRecord(record) {
  if (!confirm('Confirma eliminar este registro local?')) return
  await db.pendingRecords.delete(record.id)
  await loadRecords()
  toast.info('Registro eliminado')
}

function openDetail(record) {
  selectedRecord.value = record
  showTechnicalData.value = false
  showDetail.value = true
}

function detailField(key, label, value, type = 'text') {
  return { key, label, value, type }
}

function hasDetailValue(value) {
  return value !== null && value !== undefined && value !== '' && value !== 0 && value !== '0'
}

function synchronizationStatusLabel(record) {
  if (isFailedRecord(record)) return 'Falló sincronización'
  if (record?.syncStatus === 'syncing') return 'Sincronizando'
  return 'Pendiente de sincronización'
}

function formatDetailValue(value, type = 'text') {
  if (!hasDetailValue(value)) return '-'
  if (type === 'date') {
    const [year, month, day] = String(value).split('-')
    if (year && month && day) return `${day}/${month}/${year}`
  }
  if (type === 'number') {
    const numeric = Number(value)
    if (Number.isFinite(numeric)) {
      return numeric.toLocaleString('es-AR', { maximumFractionDigits: 2 })
    }
  }
  return String(value)
}

function formatDate(timestamp) {
  if (!timestamp) return '-'
  return new Intl.DateTimeFormat('es-AR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(timestamp))
}
</script>
