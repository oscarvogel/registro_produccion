<template>
  <div class="min-h-[calc(100vh-8.5rem)] md:min-h-[calc(100vh-3.5rem)] bg-neutral-100 px-4 py-5 md:py-6">
    <div class="mx-auto max-w-5xl space-y-4">
      <AppToolbar
        title="Registros Pendientes"
        description="Revisa la cola offline, reintenta sincronizaciones y corrige registros fallidos."
      >
        <AppBadge :tone="navigatorOnline ? 'success' : 'warning'">
          {{ navigatorOnline ? 'En linea' : 'Sin conexion' }}
        </AppBadge>
        <AppButton variant="secondary" @click="loadRecords">Refrescar</AppButton>
        <AppButton :loading="syncing" :disabled="!navigatorOnline || pendingRecords.length === 0" @click="syncAll">
          Sincronizar
        </AppButton>
      </AppToolbar>

      <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
        <div class="rounded-xl border border-neutral-200 bg-white p-4">
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Pendientes</p>
          <p class="mt-2 text-2xl font-extrabold text-primary-dark">{{ pendingRecords.length }}</p>
        </div>
        <div class="rounded-xl border border-neutral-200 bg-white p-4">
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Fallidos</p>
          <p class="mt-2 text-2xl font-extrabold text-error">{{ failedRecords.length }}</p>
        </div>
        <div class="rounded-xl border border-neutral-200 bg-white p-4">
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Total en cola</p>
          <p class="mt-2 text-2xl font-extrabold text-neutral-800">{{ records.length }}</p>
        </div>
      </div>

      <EmptyState
        v-if="!loading && records.length === 0"
        title="No hay registros en espera"
        description="Cuando cargues produccion sin conexion, los registros apareceran aca."
      />

      <div v-else class="space-y-3">
        <div v-if="loading" class="rounded-xl border border-neutral-200 bg-white p-6 text-center text-sm text-neutral-500">
          Cargando registros...
        </div>

        <div
          v-for="record in records"
          :key="record.id"
          class="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <AppBadge :tone="record.synced === 1 ? 'error' : 'warning'">
                  {{ record.synced === 1 ? 'Fallido' : 'Pendiente' }}
                </AppBadge>
                <span class="text-xs text-neutral-400">{{ formatDate(record.timestamp) }}</span>
              </div>
              <p class="mt-2 text-base font-extrabold text-neutral-900">
                {{ record.payload?.UN || 'Unidad sin definir' }} · {{ record.payload?.operacion || 'Proceso sin definir' }}
              </p>
              <p class="mt-1 text-sm text-neutral-500">
                {{ record.payload?.operador || 'Operador sin definir' }} · {{ record.payload?.equipo || 'Equipo sin definir' }}
              </p>
              <p v-if="record.syncError" class="mt-2 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                {{ record.syncError }}
              </p>
            </div>

            <div class="flex flex-wrap gap-2 md:justify-end">
              <AppButton variant="secondary" size="sm" @click="openDetail(record)">Detalle</AppButton>
              <AppButton
                variant="primary"
                size="sm"
                :disabled="!navigatorOnline || retryingId === record.id"
                :loading="retryingId === record.id"
                @click="retryRecord(record)"
              >
                Reintentar
              </AppButton>
              <AppButton variant="danger" size="sm" @click="discardRecord(record)">Descartar</AppButton>
            </div>
          </div>
        </div>
      </div>

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
import { useProduccionStore } from '@/stores/produccion'
import { useToastStore } from '@/stores/toast'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppToolbar from '@/components/ui/AppToolbar.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

const produccionStore = useProduccionStore()
const toast = useToastStore()

const records = ref([])
const loading = ref(false)
const syncing = ref(false)
const retryingId = ref(null)
const showDetail = ref(false)
const selectedRecord = ref(null)
const navigatorOnline = ref(navigator.onLine)

const pendingRecords = computed(() => records.value.filter((record) => record.synced === 0))
const failedRecords = computed(() => records.value.filter((record) => record.synced === 1))
const selectedRecordText = computed(() => JSON.stringify(selectedRecord.value?.payload || {}, null, 2))

onMounted(() => {
  loadRecords()
  window.addEventListener('online', updateOnline)
  window.addEventListener('offline', updateOnline)
})

onUnmounted(() => {
  window.removeEventListener('online', updateOnline)
  window.removeEventListener('offline', updateOnline)
})

function updateOnline() {
  navigatorOnline.value = navigator.onLine
}

async function loadRecords() {
  loading.value = true
  try {
    records.value = await db.pendingRecords.orderBy('timestamp').reverse().toArray()
    await produccionStore.refreshPendingCount()
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
  if (!confirm('Confirma descartar este registro local?')) return
  await db.pendingRecords.delete(record.id)
  await loadRecords()
  toast.info('Registro descartado')
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
