<template>
  <span :class="['inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-semibold', toneClass]">
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
    success: 'app-state-active',
    active: 'app-state-active',
    warning: 'app-state-idle',
    idle: 'app-state-idle',
    error: 'app-state-incident',
    incident: 'app-state-incident',
    info: 'app-chip-info',
    primary: 'app-chip-info',
    neutral: 'app-state-inactive',
  }
  return tones[props.tone] || tones.neutral
})
</script>
