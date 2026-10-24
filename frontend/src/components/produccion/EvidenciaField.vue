<template>
  <div class="app-surface-muted rounded-xl border border-neutral-300/70 px-3 py-3">
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0">
        <p class="text-sm font-bold text-[var(--app-text)]">{{ titulo }}</p>
        <p class="mt-0.5 text-xs text-[var(--app-text-muted)]">{{ ayuda }}</p>
      </div>
      <span
        v-if="requerido"
        class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold"
        :class="value ? 'bg-success/15 text-success-dark' : 'bg-error-light/60 text-error-dark'"
      >
        {{ value ? 'Lista' : 'Obligatoria' }}
      </span>
    </div>

    <div class="mt-3 flex items-center gap-3">
      <img
        v-if="value && value.preview"
        :src="value.preview"
        :alt="titulo"
        class="h-20 w-20 shrink-0 rounded-lg border border-neutral-300 object-cover"
      />
      <div class="flex flex-wrap items-center gap-2">
        <label
          :for="inputId"
          class="inline-flex cursor-pointer select-none items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-extrabold text-on-primary shadow-[0_4px_14px_rgba(20,61,35,0.25)] transition-colors active:bg-primary-dark"
        >
          <AppIcon name="camera" size="sm" />
          {{ value ? 'Rehacer foto' : 'Tomar foto' }}
        </label>
        <button
          v-if="value"
          type="button"
          class="app-button-soft inline-flex items-center gap-1.5 rounded-xl border px-3 py-2.5 text-sm font-bold text-[var(--app-text-muted)] hover:border-primary/30"
          @click="quitar"
        >
          <AppIcon name="delete" size="sm" />
          Quitar
        </button>
        <span v-if="procesando" class="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--app-text-muted)]">
          <AppIcon name="loading" size="xs" class="animate-spin" />
          Procesando...
        </span>
      </div>
    </div>

    <!-- capture="environment": en el telefono abre directo la camara -->
    <input
      :id="inputId"
      ref="inputRef"
      type="file"
      accept="image/*"
      capture="environment"
      class="sr-only"
      @change="onChange"
    />

    <p v-if="subtexto" class="mt-2 text-xs font-semibold text-[var(--app-text-soft)]">
      {{ subtexto }}
    </p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { comprimirImagen } from '@/utils/imagen'

const props = defineProps({
  // { file, preview, nombre } | null
  modelValue: { type: Object, default: null },
  titulo: { type: String, default: '' },
  ayuda: { type: String, default: '' },
  subtexto: { type: String, default: '' },
  requerido: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const uniqueId = Math.random().toString(36).slice(2)
const inputId = `evidencia-field-${uniqueId}`
const inputRef = ref(null)
const procesando = ref(false)
const value = computed(() => props.modelValue)

let objectUrl = null

function liberarPreview() {
  if (objectUrl && typeof URL?.revokeObjectURL === 'function') {
    URL.revokeObjectURL(objectUrl)
  }
  objectUrl = null
}

async function onChange(event) {
  const input = event.target
  const archivo = input?.files?.[0]
  // Limpiar el valor permite volver a elegir la misma foto.
  if (input) input.value = ''
  if (!archivo) return

  procesando.value = true
  try {
    const comprimida = await comprimirImagen(archivo)
    liberarPreview()
    objectUrl = URL.createObjectURL(comprimida)
    emit('update:modelValue', {
      file: comprimida,
      preview: objectUrl,
      nombre: comprimida?.name || 'evidencia.jpg',
    })
  } finally {
    procesando.value = false
  }
}

function quitar() {
  liberarPreview()
  emit('update:modelValue', null)
}

// Si el padre descarta la foto (cambio de tipo de proceso), la URL se
// libera: no queda memoria colgada de una foto que ya no se usa.
watch(() => props.modelValue, (valor) => {
  if (!valor) liberarPreview()
})

onBeforeUnmount(liberarPreview)
</script>
