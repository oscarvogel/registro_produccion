<template>
  <div
    :class="[
      'app-card-glass px-3 py-3',
      sticky ? 'fixed bottom-0 left-0 right-0 z-30 md:static md:border md:shadow-none' : 'rounded-xl border shadow-sm',
    ]"
  >
    <div class="mx-auto flex max-w-5xl flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
      <p v-if="message" class="text-xs font-semibold text-error-dark sm:max-w-md">
        {{ message }}
      </p>
      <div class="flex w-full gap-2 sm:ml-auto sm:w-auto sm:justify-end">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  sticky: { type: Boolean, default: false },
  message: { type: String, default: '' },
})
</script>
