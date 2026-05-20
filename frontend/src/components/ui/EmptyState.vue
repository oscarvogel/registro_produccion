<template>
  <div class="rounded-xl border border-dashed border-neutral-300 bg-white px-5 py-8 text-center">
    <p class="text-sm font-bold text-neutral-700">{{ title }}</p>
    <p v-if="description" class="mt-1 text-sm text-neutral-500">{{ description }}</p>
    <div v-if="$slots.default" class="mt-4">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>
