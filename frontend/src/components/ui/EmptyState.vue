<template>
  <div v-motion-panel class="app-surface rounded-xl border border-dashed px-5 py-10 text-center flex flex-col items-center justify-center">
    <div v-if="icon" class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-neutral-100 text-neutral-400">
      <AppIcon :name="icon" size="xl" />
    </div>
    <h3 class="text-base font-extrabold text-neutral-800">{{ title }}</h3>
    <p v-if="description" class="mt-1.5 max-w-sm text-sm text-neutral-500">{{ description }}</p>
    <div v-if="$slots.default" class="mt-5">
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
