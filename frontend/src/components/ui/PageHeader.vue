<template>
  <header
    v-motion-panel
    :class="[
      'rounded-xl border bg-white p-4 shadow-sm md:p-5',
      elevated ? 'border-primary/20 shadow-md' : 'border-neutral-200',
    ]"
  >
    <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div class="min-w-0">
        <div v-if="$slots.kicker || kicker" class="mb-2 flex flex-wrap items-center gap-2">
          <slot name="kicker">
            <span class="text-xs font-extrabold uppercase tracking-wide text-neutral-500">{{ kicker }}</span>
          </slot>
        </div>
        <h1 class="text-xl font-extrabold leading-tight text-primary-dark md:text-2xl">
          {{ title }}
        </h1>
        <p v-if="description" class="mt-1 max-w-3xl text-sm text-neutral-500">
          {{ description }}
        </p>
      </div>
      <div v-if="$slots.actions" class="flex flex-col gap-2 sm:flex-row sm:items-center">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  kicker: { type: String, default: '' },
  elevated: { type: Boolean, default: false },
})
</script>
