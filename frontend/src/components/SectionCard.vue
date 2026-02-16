<template>
  <div class="relative bg-neutral-100 rounded-2xl shadow-sm border border-neutral-200 p-5 overflow-hidden">
    <span class="absolute left-0 top-5 bottom-5 w-1 bg-primary rounded-r-full"></span>
    <h3 class="text-base font-bold text-primary-dark uppercase tracking-wide mb-3 pl-4">
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
