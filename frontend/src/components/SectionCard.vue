<template>
  <div class="app-card relative overflow-visible rounded-xl p-3.5 sm:p-4">
    <span class="absolute bottom-3.5 left-0 top-3.5 w-1 rounded-r-full bg-secondary sm:bottom-4 sm:top-4"></span>
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
