<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 disabled:cursor-not-allowed disabled:opacity-55',
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
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-5 py-3 text-base',
  }
  return sizes[props.size] || sizes.md
})

const variantClass = computed(() => {
  const variants = {
    primary: 'bg-primary-dark text-white hover:bg-primary focus:ring-primary/30',
    secondary: 'bg-white text-neutral-700 border border-neutral-300 hover:bg-neutral-50 focus:ring-primary/20',
    danger: 'bg-white text-error border border-error/30 hover:bg-error-light/40 focus:ring-error/20',
    ghost: 'bg-transparent text-neutral-600 hover:bg-neutral-100 focus:ring-primary/20',
  }
  return variants[props.variant] || variants.primary
})
</script>
