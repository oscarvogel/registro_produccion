<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'inline-flex min-h-10 items-center justify-center gap-2 rounded-lg font-semibold transition-all duration-150 ease-out hover:-translate-y-px focus:outline-none focus:ring-2 active:translate-y-0 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-55 disabled:hover:translate-y-0 disabled:active:scale-100',
      sizeClass,
      variantClass,
      block ? 'w-full' : '',
    ]"
  >
    <span v-if="loading" class="h-4 w-4 rounded-full border-2 border-current border-t-transparent animate-spin"></span>
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
})

const sizeClass = computed(() => {
  const sizes = {
    sm: 'min-h-9 px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'min-h-11 px-5 py-2.5 text-base',
  }
  return sizes[props.size] || sizes.md
})

const variantClass = computed(() => {
  const variants = {
    primary: 'bg-primary text-on-primary shadow-[0_0_18px_rgba(16,185,129,0.18)] hover:bg-primary-dark focus:ring-primary/30',
    secondary: 'app-button-soft border focus:ring-primary/20',
    danger: 'border border-error/35 bg-error-light text-error-dark hover:border-error/60 focus:ring-error/20',
    ghost: 'bg-transparent text-neutral-600 hover:bg-primary-light/20 hover:text-primary-dark focus:ring-primary/20',
  }
  return variants[props.variant] || variants.primary
})
</script>
