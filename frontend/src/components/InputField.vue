<template>
  <div>
    <label v-if="label" class="mb-1 flex justify-between text-sm font-semibold text-neutral-600">
      <span>{{ label }}</span>
      <span v-if="invalid" class="flex items-center gap-1 text-xs font-bold text-error">
        <AppIcon name="warning" size="xs" /> Error
      </span>
    </label>
    <div class="relative">
      <input
        :type="inputType"
        :value="modelValue"
        @input="handleInput"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :min="min"
        :max="max"
        :step="step"
        :inputmode="inputMode"
        :pattern="pattern"
        :class="[
          'app-input min-h-10 w-full rounded-lg border px-3 py-2 text-sm placeholder:text-neutral-400 focus:outline-none focus:ring-2 disabled:cursor-not-allowed disabled:border-neutral-200 disabled:bg-[var(--app-surface-muted)] disabled:text-neutral-500 disabled:opacity-100 transition-colors sm:px-3.5',
          invalid
            ? 'border-error/60 bg-error-light/10 text-error-dark focus:border-error focus:ring-error/30'
            : 'border-neutral-300 focus:border-primary/40 focus:ring-primary/30',
          invalid ? 'pr-10' : ''
        ]"
      />
      <div v-if="invalid" class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-error">
        <AppIcon name="warning" size="sm" />
      </div>
    </div>
  </div>
</template>

<script setup>
import AppIcon from '@/components/ui/AppIcon.vue'
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  min: { type: [String, Number], default: undefined },
  max: { type: [String, Number], default: undefined },
  step: { type: [String, Number], default: undefined },
  invalid: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const isNumeric = computed(() => props.type === 'number')
const inputType = computed(() => isNumeric.value ? 'text' : props.type)
const inputMode = computed(() => isNumeric.value ? 'decimal' : undefined)
const pattern = computed(() => isNumeric.value ? '[0-9]*([.,][0-9]+)?' : undefined)

function handleInput(event) {
  const rawValue = event.target.value
  const value = isNumeric.value ? rawValue.replace(',', '.') : rawValue
  if (value !== rawValue) event.target.value = value
  emit('update:modelValue', value)
}
</script>
