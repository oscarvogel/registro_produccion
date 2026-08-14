<template>
  <CaminosFormView
    v-if="unidadCaminos"
    :unidad="unidadCaminos"
    @back="volverAlFormularioHabitual"
  />

  <ProduccionLegacyFormView
    v-else
    :key="legacyKey"
  />
</template>

<script setup>
import { onUnmounted, ref } from 'vue'
import { useProduccionStore } from '@/stores/produccion'
import CaminosFormView from '@/views/CaminosFormView.vue'
import ProduccionLegacyFormView from '@/views/ProduccionLegacyFormView.vue'

const store = useProduccionStore()
const unidadCaminos = ref(null)
const legacyKey = ref(0)

function normalizar(value) {
  return String(value || '').trim().toLowerCase()
}

function buscarUnidad(unId) {
  return (store.unidadesNegocio || []).find(
    (unidad) => Number(unidad.idUnidadNegocio) === Number(unId),
  ) || null
}

// El formulario histórico ya tiene la selección de Unidad de Negocio y llama
// a fetchTiposProceso(unId) cada vez que esa selección cambia. Observamos esa
// acción para decidir únicamente si hay que entrar al modo especial de Caminos.
// No agregamos una segunda selección ni alteramos el flujo de las demás UN.
const unsubscribeAction = store.$onAction(({ name, args }) => {
  if (name !== 'fetchTiposProceso') return

  const unidad = buscarUnidad(args?.[0])
  if (normalizar(unidad?.nombre) === 'caminos') {
    unidadCaminos.value = unidad
  } else {
    unidadCaminos.value = null
  }
})

function volverAlFormularioHabitual() {
  unidadCaminos.value = null
  // Remontamos limpio el formulario habitual para que la UN pueda volver a
  // seleccionarse desde el mismo lugar de siempre.
  legacyKey.value += 1
}

onUnmounted(() => {
  unsubscribeAction()
})
</script>
