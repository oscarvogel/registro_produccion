<template>
  <div class="min-h-[calc(100vh-8.5rem)] bg-surface px-4 py-5 md:min-h-[calc(100vh-3.5rem)] md:py-6">
    <div class="mx-auto max-w-6xl space-y-4">
      <PageHeader
        title="Registros Pendientes"
        :description="scopeDescription"
      >
        <template #kicker>
          <AppBadge :tone="navigatorOnline ? 'success' : 'warning'">
            {{ navigatorOnline ? 'En linea' : 'Sin conexion' }}
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
          <AppButton :loading="syncing" :disabled="!navigatorOnline || scopedPendingRecords.length === 0" @click="syncAll">
            <AppIcon name="sync" size="sm" />
            Sincronizar
          </AppButton>
        </template>
      </PageHeader>

      <section class="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 shadow-sm">
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-xs font-extrabold uppercase tracking-wide text-on-surface-variant">Estado de sincronizacion</p>
            <h2 class="mt-1 text-xl font-extrabold text-neutral-950">{{ syncStatusTitle }}</h2>
            <p class="mt-1 text-sm text-on-surface-variant">
              {{ navigatorOnline ? 'Sistema en linea' : 'Sistema sin conexion' }} · {{ healthMessage }} · Ultima revision: {{ lastCheckLabel }}
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
          description="Registros esperando sincronizacion"
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

      <section class="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 shadow-sm">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-xs font-extrabold uppercase tracking-wide text-on-surface-variant">Cola de sincronizacion</p>
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
                  ? 'border-secondary bg-secondary text-white'
                  : 'border-outline-variant bg-white text-on-surface-variant hover:bg-surface-container-low',
              ]"
              @click="activeFilter = filter.value"
            >
              {{ filter.label }}
            </button>
          </div>
        </div>

        <div v-if="loading" class="mt-4 rounded-lg border border-outline-variant bg-surface-container-low p-6 text-center text-sm text-on-surface-variant">
          Cargando registros...
        </div>

        <div v-else-if="visibleRecords.length === 0" class="mt-4">
          <EmptyState
            title="Todo sincronizado"
            description="No hay registros pendientes ni fallidos. Las cargas realizadas se encuentran guardadas correctamente."
            icon="sync"
          >
            <p class="mt-3 text-xs font-semibold text-outline">Ultima verificacion: {{ lastCheckFullLabel }}</p>
          </EmptyState>
        </div>

        <div v-else class="mt-4 space-y-3">
          <article
            v-for="record in visibleRecords"
            :key="record.id"
            :class="[
              'rounded-xl border bg-white p-4 shadow-sm',
              isFailedRecord(record) ? 'border-error/30 bg-error-light/20' : 'border-warning/30 bg-warning-light/20',
            ]"
          >
            <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <AppBadge :tone="isFailedRecord(record) ? 'error' : 'warning'">
                    {{ isFailedRecord(record) ? 'Fallo sincronizacion' : 'Pendiente' }}
                  </AppBadge>
                  <span class="text-xs text-outline">{{ formatDate(record.timestamp) }}</span>
                </div>
                <p class="mt-2 text-base font-extrabold text-on-surface">
                  Produccion - {{ record.payload?.UN || 'Unidad sin definir' }}
                </p>
                <dl class="mt-2 grid gap-1 text-sm text-on-surface-variant sm:grid-cols-2">
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

      <section class="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 shadow-sm">
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

      <AppModal v-model="showDetail" title="Detalle del Registro" description="Payload guardado localmente para sincronizacion.">
        <pre class="max-h-[55vh] overflow-auto rounded-lg bg-neutral-900 p-4 text-xs text-white">{{ selectedRecordText }}</pre>
      </AppModal>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import api from '@/services/api'
import db from '@/services/db'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
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
const toast = useToastStore()

const records = ref([])
const loading = ref(false)
const syncing = ref(false)
const retryingId = ref(null)
const showDetail = ref(false)
const selectedRecord = ref(null)
const navigatorOnline = ref(navigator.onLine)
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

const filters = computed(() => [
  { value: 'all', label: `Todos (${scopedRecords.value.length})` },
  { value: 'pending', label: `Pendientes (${scopedPendingRecords.value.length})` },
  { value: 'failed', label: `Fallidos (${scopedFailedRecords.value.length})` },
  { value: 'recent', label: 'Sincronizados recientemente' },
])

const visibleRecords = computed(() => {
  if (activeFilter.value === 'pending') return scopedPendingRecords.value
  if (activeFilter.value === 'failed') return scopedFailedRecords.value
  if (activeFilter.value === 'recent') return []
  return scopedRecords.value
})

const scopeDescription = computed(() => {
  if (isAdmin.value) return 'Vista global de la cola disponible en este dispositivo y estado general de sincronizacion.'
  if (isEncargado.value) return 'Vista de registros pendientes o fallidos para tus unidades de negocio asignadas.'
  return 'Vista de registros pendientes o fallidos generados por tu usuario.'
})

const systemPendingLabel = computed(() => {
  if (isAdmin.value) return 'Pendientes sistema'
  if (isEncargado.value) return 'Pendientes unidad'
  return 'Mis pendientes'
})

const systemFailedLabel = computed(() => {
  if (isAdmin.value) return 'Fallidos sistema'
  if (isEncargado.value) return 'Fallidos unidad'
  return 'Mis fallidos'
})

const systemPendingDescription = computed(() => {
  if (isAdmin.value) return 'Todos los registros visibles para administracion'
  if (isEncargado.value) return 'Registros de tus unidades asignadas'
  return 'Registros creados por tu usuario'
})

const systemFailedDescription = computed(() => {
  if (isAdmin.value) return 'Errores detectados en la cola visible'
  if (isEncargado.value) return 'Errores dentro de tus unidades'
  return 'Errores de tus cargas locales'
})

const isHealthy = computed(() => navigatorOnline.value && scopedRecords.value.length === 0)
const syncStatusTitle = computed(() => {
  if (!navigatorOnline.value) return 'Sin conexion'
  if (scopedFailedRecords.value.length > 0) return 'Requiere revision'
  if (scopedPendingRecords.value.length > 0) return 'Con registros pendientes'
  return 'Todo sincronizado'
})

const healthMessage = computed(() => {
  if (!navigatorOnline.value) return 'Las nuevas cargas quedaran guardadas en este equipo'
  if (scopedFailedRecords.value.length > 0) return `${scopedFailedRecords.value.length} registro(s) fallidos`
  if (scopedPendingRecords.value.length > 0) return `${scopedPendingRecords.value.length} registro(s) esperando envio`
  return 'Sin conflictos detectados'
})

const queueTitle = computed(() => {
  if (loading.value) return 'Revisando cola offline'
  if (scopedRecords.value.length === 0) return 'Todo sincronizado'
  return `${scopedRecords.value.length} registro(s) requieren atencion`
})

const recentActivityTitle = computed(() => {
  if (scopedFailedRecords.value.length === 0) return 'No hubo intentos fallidos de sincronizacion.'
  return `${scopedFailedRecords.value.length} intento(s) fallidos detectados.`
})

const recentActivityDescription = computed(() => {
  if (scopedFailedRecords.value.length === 0) return 'La cola offline no registra errores para el alcance actual.'
  const lastFailed = [...scopedFailedRecords.value].sort((a, b) => Number(b.failedAt || b.timestamp || 0) - Number(a.failedAt || a.timestamp || 0))[0]
  return `Ultimo error: ${lastFailed?.syncError || 'sin detalle disponible'}.`
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
    const count = await produccionStore.syncPending()
    await loadRecords()
    toast.success('Sincronizacion completa', `${count || 0} registro(s) sincronizado(s).`)
  } catch {
    toast.error('No se pudo sincronizar', 'Revisa la conexion o intenta de nuevo.')
  } finally {
    syncing.value = false
  }
}

async function retryRecord(record) {
  retryingId.value = record.id
  try {
    await api.post('/api/produccion', record.payload)
    await db.pendingRecords.delete(record.id)
    await loadRecords()
    toast.success('Registro sincronizado')
  } catch (err) {
    const detail = err.response?.data?.detail || 'No se pudo sincronizar este registro.'
    const status = err.response?.status
    await db.pendingRecords.update(record.id, {
      synced: status >= 400 && status < 500 ? 1 : 0,
      syncStatus: status >= 400 && status < 500 ? 'failed' : 'pending',
      syncError: detail,
      failedAt: Date.now(),
    })
    await loadRecords()
    toast.error('Sincronizacion fallida', detail)
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
  showDetail.value = true
}

function formatDate(timestamp) {
  if (!timestamp) return '-'
  return new Intl.DateTimeFormat('es-AR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(timestamp))
}
</script>
