<template>
  <div v-motion-panel class="app-surface flex flex-col items-center justify-center rounded-xl border border-dashed px-4 py-7 text-center">
    <div v-if="icon" class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-neutral-100 text-neutral-400">
      <AppIcon :name="icon" size="lg" />
    </div>
    <h3 class="text-base font-extrabold text-neutral-800">{{ title }}</h3>
    <p v-if="description" class="mt-1.5 max-w-sm text-sm text-neutral-500">{{ description }}</p>
    <div v-if="$slots.default" class="mt-4">
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
