<template>
  <Teleport to="body">
    <Transition name="modal-backdrop">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/35 p-4"
        @click.self="close"
        @keydown.esc.stop.prevent="close"
      >
        <div
          ref="dialogRef"
          v-motion-pop
          class="app-card-glass w-full max-w-2xl rounded-xl"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          :aria-describedby="description ? descriptionId : undefined"
          tabindex="-1"
        >
          <div class="flex items-center justify-between gap-4 border-b border-neutral-200 px-4 py-3">
            <div>
              <h3 :id="titleId" class="text-lg font-extrabold text-neutral-950">{{ title }}</h3>
              <p v-if="description" :id="descriptionId" class="mt-0.5 text-xs text-neutral-500">{{ description }}</p>
            </div>
            <button class="text-sm font-semibold text-neutral-500 transition-colors hover:text-neutral-800" type="button" @click="close">
              Cerrar
            </button>
          </div>
          <div class="max-h-[72vh] overflow-y-auto p-4">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, required: true },
  description: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
const dialogRef = ref(null)
const titleId = `modal-title-${Math.random().toString(36).slice(2)}`
const descriptionId = `modal-description-${Math.random().toString(36).slice(2)}`

watch(
  () => props.modelValue,
  async (open) => {
    if (!open) return
    await nextTick()
    dialogRef.value?.focus()
  }
)

function close() {
  emit('update:modelValue', false)
}
</script>
