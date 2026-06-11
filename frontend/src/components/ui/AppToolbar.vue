<template>
  <div class="app-card flex flex-col gap-3 rounded-xl p-4 md:flex-row md:items-end md:justify-between">
    <div>
      <h2 v-if="title" class="text-lg font-extrabold text-neutral-950">{{ title }}</h2>
      <p v-if="description" class="mt-1 text-sm text-neutral-500">{{ description }}</p>
    </div>
    <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
})
</script>
