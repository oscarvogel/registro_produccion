<template>
  <section class="app-card rounded-xl p-3 md:p-4">
    <div v-if="title || $slots.summary" class="mb-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
      <div>
        <p v-if="eyebrow" class="text-xs font-bold uppercase tracking-wide text-neutral-400">{{ eyebrow }}</p>
        <h2 v-if="title" class="text-sm font-bold text-neutral-900">{{ title }}</h2>
      </div>
      <div v-if="$slots.summary" class="flex flex-wrap gap-2">
        <slot name="summary" />
      </div>
    </div>
    <div class="grid gap-3 md:flex md:flex-wrap md:items-end">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
})
</script>
