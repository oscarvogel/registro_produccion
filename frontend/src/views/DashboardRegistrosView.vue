<template>
  <div class="min-h-screen bg-[var(--app-bg)] px-3 py-3 pb-20 md:px-4 md:py-4 md:pb-6">
    <div class="mx-auto max-w-[112rem] space-y-3">
      <PageHeader
        title="Detalle de registros"
        :description="`${authStore.userName} · registros individuales que componen el dashboard`"
        :kicker="`Unidad: ${unidadNombre || '—'}`"
      >
        <template #actions>
          <AppButton variant="secondary" @click="volverAlDashboard">
            <AppIcon name="back" size="sm" />
            Volver al dashboard
          </AppButton>
        </template>
      </PageHeader>

      <FilterBar title="Filtros transferidos" eyebrow="Aplicados desde el dashboard">
        <template #summary>
          <span class="rounded-full border px-3 py-1 text-xs font-bold app-chip-info">
            {{ store.total }} registro{{ store.total === 1 ? '' : 's' }}
          </span>
        </template>
        <div class="flex flex-wrap items-center gap-2 md:w-full">
          <span
            v-for="chip in activeFilterChips"
            :key="chip.label"
            class="rounded-full border border-neutral-200 px-3 py-1.5 text-xs font-bold"
            :class="chip.tone === 'info' ? 'app-chip-info' : 'app-state-inactive'"
          >
            {{ chip.label }}
          </span>
          <span
            v-if="!activeFilterChips.length"
            class="text-xs text-neutral-400"
          >
            Sin filtros extra: la unidad y el período ya están aplicados.
          </span>
        </div>
      </FilterBar>

      <section
        v-if="store.loading"
        class="flex justify-center py-10"
        data-testid="registros-loading"
      >
        <div class="h-8 w-8 animate-spin rounded-full border-3 border-primary border-t-transparent"></div>
      </section>

      <EmptyState
        v-else-if="store.error"
        title="No se pudieron cargar los registros"
        :description="store.error"
        icon="warning"
      />

      <EmptyState
        v-else-if="!store.hasRegistros"
        title="No hay registros para los filtros aplicados"
        description="Volvé al dashboard, modificá el rango de fechas, la unidad o el tipo de proceso."
        icon="empty"
      />

      <div v-else class="space-y-3" data-testid="registros-content">
        <DataTable
          :rows="store.registros"
          :columns="columns"
          :loading="false"
          empty-text="Sin registros para los filtros aplicados"
          row-key="id"
        >
          <template #cell-fecha="{ value }">{{ formatFecha(value) }}</template>
          <template #cell-operacion="{ value }">{{ value || 'Producción' }}</template>
          <template #cell-equipo="{ value }">{{ value || 'Sin equipo' }}</template>
          <template #cell-operador="{ value }">{{ value || 'Sin operador' }}</template>
          <template #cell-combustible="{ value }">
            <span :class="Number(value) > 0 ? 'font-extrabold text-warning-dark' : ''">
              {{ formatNumero(value) }} lts
            </span>
          </template>
          <template #cell-tn_despachadas="{ value }">{{ formatNumero(value) }} TN</template>
          <template #cell-m3="{ value }">{{ formatNumero(value) }} m3</template>
          <template #cell-has="{ value }">{{ formatNumero(value) }} has</template>
          <template #cell-km_carreteo="{ value }">{{ formatNumero(value) }} km</template>
          <template #cell-acciones="{ row }">
            <button
              type="button"
              class="rounded-md border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-700 hover:border-secondary/40"
              @click="abrirDetalle(row.id)"
              :data-testid="`abrir-detalle-${row.id}`"
            >
              Ver detalle
            </button>
          </template>
        </DataTable>

        <nav
          v-if="store.totalPages > 1"
          class="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-neutral-200 bg-white px-3 py-2"
          data-testid="paginacion"
        >
          <span class="text-xs font-bold text-neutral-500">
            Página {{ store.page }} de {{ store.totalPages }} · {{ store.total }} registros
          </span>
          <div class="flex flex-wrap items-center gap-1.5">
            <button
              type="button"
              class="rounded-md border px-2.5 py-1 text-xs font-bold disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="store.page <= 1"
              @click="store.setPage(1)"
            >
              « Primero
            </button>
            <button
              type="button"
              class="rounded-md border px-2.5 py-1 text-xs font-bold disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="store.page <= 1"
              @click="store.setPage(store.page - 1)"
            >
              ‹ Anterior
            </button>
            <span class="px-2 text-xs font-bold text-neutral-600">
              {{ store.page }}
            </span>
            <button
              type="button"
              class="rounded-md border px-2.5 py-1 text-xs font-bold disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="store.page >= store.totalPages"
              @click="store.setPage(store.page + 1)"
            >
              Siguiente ›
            </button>
            <button
              type="button"
              class="rounded-md border px-2.5 py-1 text-xs font-bold disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="store.page >= store.totalPages"
              @click="store.setPage(store.totalPages)"
            >
              Última »
            </button>
          </div>
        </nav>
      </div>
    </div>

    <RecordDetailModal
      v-model="detalleOpen"
      :registro-id="detalleId"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDashboardRegistrosStore } from '@/stores/dashboardRegistros'
import { useDashboardStore } from '@/stores/dashboard'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import DataTable from '@/components/ui/DataTable.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import FilterBar from '@/components/ui/FilterBar.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import RecordDetailModal from '@/components/registros/RecordDetailModal.vue'

const authStore = useAuthStore()
const store = useDashboardRegistrosStore()
const dashboardStore = useDashboardStore()
const route = useRoute()
const router = useRouter()

const detalleOpen = ref(false)
const detalleId = ref(null)

const columns = [
  { key: 'fecha', label: 'Fecha', sortable: true },
  { key: 'operacion', label: 'Operación', sortable: true },
  { key: 'equipo', label: 'Máquina' },
  { key: 'operador', label: 'Operador' },
  { key: 'hr_inicio', label: 'Hr inicio' },
  { key: 'hr_fin', label: 'Hr fin' },
  { key: 'combustible', label: 'Combustible' },
  { key: 'tn_despachadas', label: 'TN' },
  { key: 'm3', label: 'm³' },
  { key: 'has', label: 'Has' },
  { key: 'km_carreteo', label: 'KM carr.' },
  { key: 'acciones', label: '', sortable: false },
]

const unidadNombre = computed(() => {
  const unId = store.filtros.unId
  if (!unId) return ''
  return (
    dashboardStore.unidadesNegocio.find(
      (unidad) => Number(unidad.idUnidadNegocio) === Number(unId),
    )?.nombre || ''
  )
})

const activeFilterChips = computed(() => {
  const chips = []
  const filtros = store.filtros
  if (unidadNombre.value) chips.push({ label: `Unidad: ${unidadNombre.value}`, tone: 'info' })
  if (filtros.tipoProcesoId || filtros.tipoProcesoKey) {
    const tp = dashboardStore.tiposProceso.find(
      (item) =>
        String(item.value) === String(filtros.tipoProcesoKey) ||
        Number(item.id) === Number(filtros.tipoProcesoId),
    )
    if (tp) chips.push({ label: `Proceso: ${tp.nombre}`, tone: 'info' })
  }
  if (filtros.movilId) {
    const movil = dashboardStore.movilesDisponibles.find(
      (item) => Number(item.idMovil) === Number(filtros.movilId),
    )
    if (movil) {
      const patente = movil.patente || ''
      const detalle = movil.detalle || ''
      chips.push({
        label: `Máquina: ${[patente, detalle].filter(Boolean).join(' - ')}`,
        tone: 'info',
      })
    }
  }
  if (filtros.fechaDesde) chips.push({ label: `Desde: ${formatFecha(filtros.fechaDesde)}` })
  if (filtros.fechaHasta) chips.push({ label: `Hasta: ${formatFecha(filtros.fechaHasta)}` })
  return chips
})

function formatFecha(fecha) {
  if (!fecha) return '-'
  const str = String(fecha)
  const [y, m, d] = str.split('-')
  if (y && m && d) return `${d}/${m}/${y}`
  return str
}

function formatNumero(valor) {
  const n = Number(valor)
  if (!Number.isFinite(n) || n === 0) return '0'
  if (Number.isInteger(n)) return n.toLocaleString('es-AR')
  return n.toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 2 })
}

function abrirDetalle(id) {
  detalleId.value = id
  detalleOpen.value = true
}

function volverAlDashboard() {
  router.push({ name: 'dashboard' })
}

onMounted(async () => {
  // Aseguramos que el store del dashboard tenga las unidades/tipos para
  // resolver los nombres que se muestran en los chips.
  if (!dashboardStore.unidadesNegocio.length) {
    await dashboardStore.loadUnidadesNegocio()
  }
  const unId = route.query.un_id ? Number(route.query.un_id) : null
  if (unId && !dashboardStore.tiposProceso.length) {
    await dashboardStore.loadTiposProceso(unId)
  }
  if (unId && !dashboardStore.movilesDisponibles.length) {
    await dashboardStore.loadMovilesDisponibles(unId)
  }
  await store.initFromQuery(route.query)
})
</script>
