<template>
  <div class="fixed right-3 top-3 z-[70] flex w-[calc(100vw-1.5rem)] max-w-sm flex-col gap-2">
    <div
      v-for="toast in toastStore.items"
      :key="toast.id"
      :class="[
        'rounded-xl border bg-white px-4 py-3 shadow-lg',
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
  </div>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

function toneClass(tone) {
  const tones = {
    success: 'border-emerald-200 text-emerald-800',
    error: 'border-red-200 text-red-800',
    info: 'border-blue-200 text-blue-800',
    warning: 'border-amber-200 text-amber-800',
    neutral: 'border-neutral-200 text-neutral-800',
  }
  return tones[tone] || tones.neutral
}
</script>
