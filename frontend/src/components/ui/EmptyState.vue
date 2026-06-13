<template>
  <div v-motion-panel class="app-surface flex flex-col items-center justify-center rounded-xl border border-dashed px-4 py-5 text-center">
    <div v-if="icon" class="app-surface-muted mx-auto mb-2.5 flex h-10 w-10 items-center justify-center rounded-lg text-neutral-400">
      <AppIcon :name="icon" size="lg" />
    </div>
    <h3 class="text-base font-extrabold text-neutral-800">{{ title }}</h3>
    <p v-if="description" class="mt-1 max-w-md text-sm text-neutral-500">{{ description }}</p>
    <div v-if="$slots.default" class="mt-3">
      <slot />
    </div>
  </div>
</template>

<script setup>
import AppIcon from '@/components/ui/AppIcon.vue'

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  icon: { type: String, default: 'empty' },
})
</script>
