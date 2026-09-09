<template>
  <div
    :class="[
      'flex items-start gap-2 rounded-lg border px-3 py-2.5 text-sm font-semibold',
      toneClass,
    ]"
    :role="role"
    :aria-live="ariaLive"
    :aria-busy="tone === 'loading' ? true : undefined"
  >
    <span class="mt-0.5 shrink-0" aria-hidden="true">
      <span v-if="tone === 'loading'" class="block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
      <AppIcon v-else :name="iconName" size="sm" />
    </span>
    <div class="min-w-0 flex-1">
      <p v-if="title" class="font-bold">{{ title }}</p>
      <p v-if="message">{{ message }}</p>
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps({
  tone: { type: String, default: 'info' },
  title: { type: String, default: '' },
  message: { type: String, default: '' },
})

const toneClass = computed(() => ({
  loading: 'border-info/30 bg-info-light/40 text-info-dark',
  error: 'border-error/35 bg-error-light/30 text-error-dark',
  success: 'border-success/30 bg-success-light/40 text-success-dark',
  warning: 'border-warning/30 bg-warning-light/40 text-warning-dark',
  info: 'border-info/30 bg-info-light/40 text-info-dark',
}[props.tone] || 'border-info/30 bg-info-light/40 text-info-dark'))

const iconName = computed(() => ({
  error: 'error',
  success: 'success',
  warning: 'warning',
  info: 'info',
}[props.tone] || 'info'))

const role = computed(() => props.tone === 'error' ? 'alert' : 'status')
const ariaLive = computed(() => props.tone === 'error' ? 'assertive' : 'polite')
</script>
