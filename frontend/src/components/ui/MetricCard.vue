<template>
  <article
    v-motion-panel
    :class="[
      'app-card grid min-h-[5.75rem] grid-cols-[auto_minmax(0,1fr)] items-center gap-3 rounded-xl p-3.5 transition-all duration-150 ease-out',
      interactive ? 'app-hover-glow hover:-translate-y-px' : '',
      toneClass,
    ]"
  >
    <span v-if="icon" :class="['flex h-11 w-11 shrink-0 items-center justify-center rounded-xl', iconClass]">
      <AppIcon :name="icon" size="sm" />
    </span>
    <div class="min-w-0">
      <p class="truncate text-xs font-bold uppercase tracking-wide text-neutral-500">
        {{ label }}
      </p>
      <div class="mt-1 flex items-baseline gap-1.5">
        <span class="text-2xl font-extrabold leading-none text-neutral-900 md:text-[1.75rem]">
          {{ value }}
        </span>
        <span v-if="unit" class="text-xs font-bold text-neutral-400">{{ unit }}</span>
      </div>
      <p v-if="description" class="mt-1 truncate text-xs text-neutral-500">
        {{ description }}
      </p>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  unit: { type: String, default: '' },
  description: { type: String, default: '' },
  icon: { type: String, default: '' },
  tone: { type: String, default: 'neutral' },
  interactive: { type: Boolean, default: false },
})

const toneClass = computed(() => {
  const tones = {
    neutral: 'border-neutral-200',
    primary: 'border-primary/20',
    success: 'border-success/25 bg-success-light/20',
    info: 'border-info/25 bg-info-light/20',
    warning: 'border-warning/30 bg-warning-light/25',
    error: 'border-error/25 bg-error-light/25',
  }
  return tones[props.tone] || tones.neutral
})

const iconClass = computed(() => {
  const tones = {
    neutral: 'bg-neutral-100 text-neutral-600',
    primary: 'bg-primary-light text-primary-dark',
    success: 'bg-success-light/45 text-success-dark',
    info: 'bg-info-light text-info-dark',
    warning: 'bg-warning-light text-warning-dark',
    error: 'bg-error-light text-error-dark',
  }
  return tones[props.tone] || tones.neutral
})
</script>
