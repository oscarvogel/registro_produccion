<template>
  <div class="app-card flex flex-col gap-2.5 rounded-xl p-3.5 md:flex-row md:items-center md:justify-between">
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
