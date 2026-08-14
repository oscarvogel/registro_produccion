<template>
  <CaminosFormView
    v-if="unidadSeleccionada && esCaminos"
    :unidad="unidadSeleccionada"
    @back="cambiarUnidad"
  />

  <ProduccionLegacyFormView
    v-else-if="unidadSeleccionada"
    :key="`legacy-${unidadSeleccionada.idUnidadNegocio}`"
  />

  <div v-else class="mx-auto max-w-3xl px-3 py-5 md:px-5">
    <div class="app-card rounded-2xl p-5">
      <div class="mb-5">
        <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Carga de producción</p>
        <h1 class="mt-1 text-2xl font-extrabold text-neutral-900">¿Para qué unidad vas a cargar?</h1>
        <p class="mt-2 text-sm text-neutral-500">
          Caminos usa un parte diario con varios procesos. Las demás unidades mantienen el formulario actual.
        </p>
      </div>

      <div v-if="store.loading" class="py-10 text-center text-sm text-neutral-500">
        Cargando unidades de negocio…
      </div>

      <div v-else class="grid gap-3 sm:grid-cols-2">
        <button
          v-for="unidad in unidadesDisponibles"
          :key="unidad.idUnidadNegocio"
          type="button"
          class="app-button-soft rounded-xl border p-4 text-left transition-colors hover:border-primary/40"
          @click="seleccionarUnidad(unidad)"
        >
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Unidad de negocio</p>
          <p class="mt-1 text-lg font-extrabold text-neutral-900">{{ unidad.nombre }}</p>
          <p v-if="normalizar(unidad.nombre) === 'caminos'" class="mt-2 text-xs font-semibold text-primary-dark">
            Parte multi-proceso
          </p>
          <p v-else class="mt-2 text-xs text-neutral-500">Formulario de producción habitual</p>
        </button>
      </div>

      <div v-if="!store.loading && unidadesDisponibles.length === 0" class="rounded-xl border border-warning/30 bg-warning-light/40 p-4 text-sm text-warning-dark">
        No hay unidades de negocio disponibles para este usuario.
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import CaminosFormView from '@/views/CaminosFormView.vue'
import ProduccionLegacyFormView from '@/views/ProduccionLegacyFormView.vue'

const authStore = useAuthStore()
const store = useProduccionStore()
const unidadSeleccionada = ref(null)
const unidadesDisponibles = computed(() => store.unidadesNegocio || [])
const esCaminos = computed(() => normalizar(unidadSeleccionada.value?.nombre) === 'caminos')

function normalizar(value) {
  return String(value || '').trim().toLowerCase()
}

function preferenciasKey() {
  return `produccion_preferencias_${authStore.user?.idPersonal || 'anon'}`
}

function guardarUnidadParaLegacy(unidad) {
  try {
    const key = preferenciasKey()
    const previas = JSON.parse(localStorage.getItem(key) || '{}')
    localStorage.setItem(key, JSON.stringify({
      ...previas,
      un_id: unidad.idUnidadNegocio,
    }))
  } catch {
    // El formulario legacy puede continuar sin preferencias persistidas.
  }
}

function seleccionarUnidad(unidad) {
  if (normalizar(unidad?.nombre) !== 'caminos') {
    guardarUnidadParaLegacy(unidad)
  }
  unidadSeleccionada.value = unidad
}

function cambiarUnidad() {
  unidadSeleccionada.value = null
}

function unidadPreferida() {
  try {
    const preferencias = JSON.parse(localStorage.getItem(preferenciasKey()) || '{}')
    return unidadesDisponibles.value.find(
      (unidad) => Number(unidad.idUnidadNegocio) === Number(preferencias.un_id),
    ) || null
  } catch {
    return null
  }
}

onMounted(async () => {
  await store.loadCatalogos()

  if (unidadesDisponibles.value.length === 1) {
    seleccionarUnidad(unidadesDisponibles.value[0])
    return
  }

  const userUnits = Array.isArray(authStore.user?.unidad_ids) ? authStore.user.unidad_ids : []
  if (userUnits.length === 1) {
    const unica = unidadesDisponibles.value.find(
      (unidad) => Number(unidad.idUnidadNegocio) === Number(userUnits[0]),
    )
    if (unica) {
      seleccionarUnidad(unica)
      return
    }
  }

  const preferida = unidadPreferida()
  if (preferida) seleccionarUnidad(preferida)
})
</script>
