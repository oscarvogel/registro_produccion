<template>
  <div class="app-card relative overflow-visible rounded-xl p-5">
    <span class="absolute left-0 top-5 bottom-5 w-1 bg-secondary rounded-r-full"></span>
    <h3 class="text-base font-bold text-neutral-900 uppercase tracking-wide mb-3 pl-4">
      {{ title }}
    </h3>
    <div class="pl-4">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
})
</script>
