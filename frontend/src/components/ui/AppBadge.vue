<template>
  <span :class="['inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-bold', toneClass]">
    <slot />
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tone: { type: String, default: 'neutral' },
})

const toneClass = computed(() => {
  const tones = {
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    error: 'bg-red-50 text-red-700 border-red-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    primary: 'bg-primary/10 text-primary-dark border-primary/20',
    neutral: 'bg-neutral-100 text-neutral-600 border-neutral-200',
  }
  return tones[props.tone] || tones.neutral
})
</script>
