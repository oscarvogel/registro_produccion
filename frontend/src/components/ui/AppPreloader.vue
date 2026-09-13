<template>
  <div class="app-preloader flex min-h-[12rem] items-center justify-center gap-3 p-6" role="status" aria-live="polite">
    <span class="motion-safe:animate-spin h-5 w-5 rounded-full border-2 border-primary border-t-transparent" aria-hidden="true"></span>
    <span class="text-sm font-semibold text-[var(--app-text-muted)]">{{ label }}</span>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, default: 'Cargando pantalla...' },
})
</script>
