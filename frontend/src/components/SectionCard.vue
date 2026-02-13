<template>
  <div class="bg-white rounded-xl shadow-sm border border-neutral-200 p-5">
    <h3 class="text-sm font-semibold text-primary-dark uppercase tracking-wide mb-3 flex items-center gap-2">
      <span class="w-1 h-4 bg-primary rounded-full"></span>
      {{ title }}
    </h3>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
})
</script>
