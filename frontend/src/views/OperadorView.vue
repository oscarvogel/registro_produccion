<template>
  <div class="min-h-screen bg-neutral-100 pb-24 md:pb-8">
    <!-- Header -->
    <div class="bg-white border-b border-neutral-200 shadow-sm">
      <div class="max-w-3xl mx-auto px-4 py-4 flex items-center gap-3">
        <button @click="$router.back()" aria-label="Volver" title="Volver" class="p-2 rounded-xl hover:bg-neutral-100 transition-colors text-neutral-500">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div>
          <h1 class="text-lg font-extrabold text-primary-dark">Mis Registros</h1>
          <p class="text-xs text-neutral-500">{{ authStore.userName }}</p>
        </div>
      </div>
    </div>

    <!-- Filtros de fecha -->
    <div class="bg-white border-b border-neutral-200 shadow-sm">
      <div class="max-w-3xl mx-auto px-4 py-3 flex items-end gap-3 flex-wrap">
        <div class="flex-1 min-w-36">
          <label class="block text-xs font-medium text-neutral-500 mb-1">Desde</label>
          <input
            type="date"
            :value="store.filtros.fecha_desde"
            @change="store.setFiltro('fecha_desde', $event.target.value || null)"
            class="w-full px-3 py-2 text-sm bg-neutral-50 border border-neutral-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/40"
          />
        </div>
        <div class="flex-1 min-w-36">
          <label class="block text-xs font-medium text-neutral-500 mb-1">Hasta</label>
          <input
            type="date"
            :value="store.filtros.fecha_hasta"
            @change="store.setFiltro('fecha_hasta', $event.target.value || null)"
            class="w-full px-3 py-2 text-sm bg-neutral-50 border border-neutral-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/40"
          />
        </div>
        <button
          @click="store.limpiarFiltros()"
          class="px-4 py-2 text-sm font-medium text-neutral-500 hover:text-neutral-700 border border-neutral-300 rounded-xl hover:bg-neutral-50 transition-colors whitespace-nowrap"
        >
          Este mes
        </button>
      </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">

      <!-- Loading -->
      <div v-if="store.loading" class="flex justify-center py-16">
        <div class="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>

      <template v-else>
        <!-- Totales -->
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-white rounded-2xl border border-neutral-200 p-4">
            <p class="text-xs font-medium text-neutral-500 mb-1">Registros</p>
            <p class="text-2xl font-extrabold text-neutral-900">{{ store.totales.total }}</p>
          </div>
          <div class="bg-white rounded-2xl border border-neutral-200 p-4">
            <p class="text-xs font-medium text-neutral-500 mb-1">Horas trabajadas</p>
            <p class="text-2xl font-extrabold text-neutral-900">{{ fmt(store.totales.total_horas) }} <span class="text-sm font-medium text-neutral-400">hs</span></p>
          </div>
          <div class="bg-white rounded-2xl border border-neutral-200 p-4">
            <p class="text-xs font-medium text-neutral-500 mb-1">Combustible</p>
            <p class="text-2xl font-extrabold text-neutral-900">{{ store.totales.total_combustible }} <span class="text-sm font-medium text-neutral-400">lts</span></p>
          </div>
          <div v-if="store.totales.combustible_por_hora != null" class="bg-white rounded-2xl border border-neutral-200 p-4">
            <p class="text-xs font-medium text-neutral-500 mb-1">Combustible / hora</p>
            <p class="text-2xl font-extrabold text-neutral-900">{{ fmt(store.totales.combustible_por_hora) }} <span class="text-sm font-medium text-neutral-400">lts/hs</span></p>
          </div>

          <!-- Producción: mostramos solo los campos con valor > 0 -->
          <div v-if="store.totales.total_tn > 0" class="bg-primary/5 border border-primary/20 rounded-2xl p-4">
            <p class="text-xs font-medium text-primary-dark mb-1">Toneladas despachadas</p>
            <p class="text-2xl font-extrabold text-primary-dark">{{ fmt(store.totales.total_tn) }} <span class="text-sm font-medium text-primary/60">TN</span></p>
            <p v-if="store.totales.tn_por_hora != null" class="text-xs text-primary/60 mt-1">{{ fmt(store.totales.tn_por_hora) }} TN/hs</p>
          </div>
          <div v-if="store.totales.total_m3 > 0" class="bg-primary/5 border border-primary/20 rounded-2xl p-4">
            <p class="text-xs font-medium text-primary-dark mb-1">Metros cúbicos</p>
            <p class="text-2xl font-extrabold text-primary-dark">{{ store.totales.total_m3 }} <span class="text-sm font-medium text-primary/60">M³</span></p>
            <p v-if="store.totales.m3_por_hora != null" class="text-xs text-primary/60 mt-1">{{ fmt(store.totales.m3_por_hora) }} M³/hs</p>
          </div>
          <div v-if="store.totales.total_has > 0" class="bg-primary/5 border border-primary/20 rounded-2xl p-4">
            <p class="text-xs font-medium text-primary-dark mb-1">Hectáreas</p>
            <p class="text-2xl font-extrabold text-primary-dark">{{ fmt(store.totales.total_has) }} <span class="text-sm font-medium text-primary/60">HAS</span></p>
            <p v-if="store.totales.has_por_hora != null" class="text-xs text-primary/60 mt-1">{{ fmt(store.totales.has_por_hora) }} HAS/hs</p>
          </div>
          <div v-if="store.totales.total_carros > 0" class="bg-primary/5 border border-primary/20 rounded-2xl p-4">
            <p class="text-xs font-medium text-primary-dark mb-1">Carros</p>
            <p class="text-2xl font-extrabold text-primary-dark">{{ store.totales.total_carros }} <span class="text-sm font-medium text-primary/60">uds</span></p>
            <p v-if="store.totales.carros_por_hora != null" class="text-xs text-primary/60 mt-1">{{ fmt(store.totales.carros_por_hora) }} carros/hs</p>
          </div>
          <div v-if="store.totales.total_plantas > 0" class="bg-primary/5 border border-primary/20 rounded-2xl p-4">
            <p class="text-xs font-medium text-primary-dark mb-1">Plantas</p>
            <p class="text-2xl font-extrabold text-primary-dark">{{ store.totales.total_plantas }} <span class="text-sm font-medium text-primary/60">uds</span></p>
            <p v-if="store.totales.plantas_por_hora != null" class="text-xs text-primary/60 mt-1">{{ fmt(store.totales.plantas_por_hora) }} plantas/hs</p>
          </div>
          <div v-if="store.totales.total_km_carreteo > 0" class="bg-primary/5 border border-primary/20 rounded-2xl p-4">
            <p class="text-xs font-medium text-primary-dark mb-1">KM Carreteo</p>
            <p class="text-2xl font-extrabold text-primary-dark">{{ fmt(store.totales.total_km_carreteo) }} <span class="text-sm font-medium text-primary/60">km</span></p>
            <p v-if="store.totales.km_carreteo_por_hora != null" class="text-xs text-primary/60 mt-1">{{ fmt(store.totales.km_carreteo_por_hora) }} km/hs</p>
          </div>
          <div v-if="store.totales.total_km_perfilado > 0" class="bg-primary/5 border border-primary/20 rounded-2xl p-4">
            <p class="text-xs font-medium text-primary-dark mb-1">KM Perfilado</p>
            <p class="text-2xl font-extrabold text-primary-dark">{{ fmt(store.totales.total_km_perfilado) }} <span class="text-sm font-medium text-primary/60">km</span></p>
            <p v-if="store.totales.km_perfilado_por_hora != null" class="text-xs text-primary/60 mt-1">{{ fmt(store.totales.km_perfilado_por_hora) }} km/hs</p>
          </div>
        </div>

        <!-- Lista de registros -->
        <div v-if="store.registros.length > 0" class="space-y-2">
          <h2 class="text-xs font-bold text-neutral-500 uppercase tracking-wide px-1">Detalle de registros</h2>
          <div
            v-for="r in store.registros"
            :key="r.id"
            class="bg-white rounded-2xl border border-neutral-200 p-4"
          >
            <div class="flex items-start justify-between gap-2 mb-2">
              <div>
                <span class="inline-block px-2 py-0.5 rounded-lg bg-primary/10 text-primary-dark text-xs font-bold uppercase tracking-wide">{{ r.operacion || '—' }}</span>
                <p class="text-xs text-neutral-400 mt-1">{{ formatFecha(r.fecha) }}</p>
              </div>
              <p class="text-xs text-neutral-500 text-right">{{ r.equipo || '—' }}</p>
            </div>
            <div class="flex flex-wrap gap-3 mt-2">
              <!-- Producción: solo campos con valor -->
              <span v-if="r.tn_despachadas > 0" class="text-sm font-semibold text-neutral-700">{{ fmt(r.tn_despachadas) }} <span class="font-normal text-neutral-400">TN</span></span>
              <span v-if="r.m3 > 0" class="text-sm font-semibold text-neutral-700">{{ r.m3 }} <span class="font-normal text-neutral-400">M³</span></span>
              <span v-if="r.has > 0" class="text-sm font-semibold text-neutral-700">{{ fmt(r.has) }} <span class="font-normal text-neutral-400">HAS</span></span>
              <span v-if="r.carros > 0" class="text-sm font-semibold text-neutral-700">{{ r.carros }} <span class="font-normal text-neutral-400">carros</span></span>
              <span v-if="r.plantas > 0" class="text-sm font-semibold text-neutral-700">{{ r.plantas }} <span class="font-normal text-neutral-400">plantas</span></span>
              <span v-if="r.km_carreteo > 0" class="text-sm font-semibold text-neutral-700">{{ fmt(r.km_carreteo) }} <span class="font-normal text-neutral-400">km carr.</span></span>
              <span v-if="r.km_perfilado > 0" class="text-sm font-semibold text-neutral-700">{{ fmt(r.km_perfilado) }} <span class="font-normal text-neutral-400">km perf.</span></span>
              <!-- Combustible siempre visible si > 0 -->
              <span v-if="r.combustible > 0" class="text-sm font-semibold text-warning-dark">{{ r.combustible }} <span class="font-normal text-neutral-400">lts</span></span>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div v-else class="bg-white rounded-2xl border border-neutral-200 p-10 text-center">
          <svg class="mx-auto mb-4 w-14 h-14 text-neutral-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <path d="M3 9h18M9 21V9"/>
          </svg>
          <p class="text-neutral-500 font-medium">No hay registros para este período</p>
          <p class="text-neutral-400 text-sm mt-1">Probá con otro rango de fechas</p>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMisRegistrosStore } from '@/stores/misRegistros'

const authStore = useAuthStore()
const store = useMisRegistrosStore()

function fmt(val) {
  return Number(val).toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function formatFecha(fecha) {
  if (!fecha) return '—'
  const [y, m, d] = fecha.split('-')
  return `${d}/${m}/${y}`
}

onMounted(() => {
  store.initFiltros()
  store.fetchMisRegistros()
})
</script>
