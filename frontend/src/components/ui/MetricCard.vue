<template>
  <article
    v-motion-panel
    :class="[
      'rounded-xl border bg-white p-4 shadow-sm transition-all duration-150 ease-out',
      interactive ? 'hover:-translate-y-px hover:shadow-md' : '',
      toneClass,
    ]"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="truncate text-xs font-extrabold uppercase tracking-wide text-neutral-500">
          {{ label }}
        </p>
        <div class="mt-2 flex items-baseline gap-1.5">
          <span class="text-2xl font-extrabold leading-none text-neutral-900 md:text-3xl">
            {{ value }}
          </span>
          <span v-if="unit" class="text-sm font-bold text-neutral-400">{{ unit }}</span>
        </div>
      </div>
      <span v-if="icon" :class="['flex h-10 w-10 shrink-0 items-center justify-center rounded-xl', iconClass]">
        <AppIcon :name="icon" size="sm" />
      </span>
    </div>
    <p v-if="description" class="mt-2 text-sm text-neutral-500">
      {{ description }}
    </p>
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
    primary: 'border-primary/20 bg-primary-light/10',
    success: 'border-success/20 bg-success-light/20',
    warning: 'border-warning/30 bg-warning-light/30',
    error: 'border-error/20 bg-error-light/30',
  }
  return tones[props.tone] || tones.neutral
})

const iconClass = computed(() => {
  const tones = {
    neutral: 'bg-neutral-100 text-neutral-600',
    primary: 'bg-primary-light/35 text-primary-dark',
    success: 'bg-success-light/40 text-success-dark',
    warning: 'bg-warning-light text-warning-dark',
    error: 'bg-error-light text-error-dark',
  }
  return tones[props.tone] || tones.neutral
})
</script>
