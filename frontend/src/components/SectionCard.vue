<template>
  <div class="app-card relative overflow-visible rounded-xl p-4">
    <span class="absolute bottom-4 left-0 top-4 w-1 rounded-r-full bg-secondary"></span>
    <h3 class="mb-2.5 pl-3 text-sm font-bold uppercase tracking-wide text-neutral-900">
      {{ title }}
    </h3>
    <div class="pl-3">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
})
</script>
