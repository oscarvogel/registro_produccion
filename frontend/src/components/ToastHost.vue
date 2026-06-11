<template>
  <TransitionGroup
    name="toast-list"
    tag="div"
    class="fixed right-3 top-3 z-[70] flex w-[calc(100vw-1.5rem)] max-w-sm flex-col gap-2"
  >
    <div
      v-for="toast in toastStore.items"
      :key="toast.id"
      v-motion-pop
      :class="[
        'app-card-glass rounded-xl px-4 py-3 will-change-transform',
        toneClass(toast.tone),
      ]"
    >
      <div class="flex items-start justify-between gap-3">
        <div>
          <p class="text-sm font-extrabold">{{ toast.title }}</p>
          <p v-if="toast.message" class="mt-0.5 text-sm opacity-80">{{ toast.message }}</p>
        </div>
        <button
          type="button"
          class="text-xs font-bold opacity-60 hover:opacity-100"
          @click="toastStore.remove(toast.id)"
        >
          Cerrar
        </button>
      </div>
    </div>
  </TransitionGroup>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

function toneClass(tone) {
  const tones = {
    success: 'app-state-active',
    error: 'app-state-incident',
    info: 'app-chip-info',
    warning: 'app-state-idle',
    neutral: 'app-state-inactive',
  }
  return tones[tone] || tones.neutral
}
</script>
