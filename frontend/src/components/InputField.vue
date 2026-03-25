<template>
  <div>
    <label v-if="label" class="block text-sm font-medium text-neutral-600 mb-1.5">
      {{ label }}
    </label>
    <input
      :type="type"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :min="min"
      :max="max"
      :class="[
        'w-full px-4 py-3 bg-neutral-100 border rounded-xl text-neutral-900 placeholder:text-neutral-400 focus:outline-none focus:ring-2 disabled:bg-neutral-200 disabled:cursor-not-allowed transition-colors',
        invalid
          ? 'border-error focus:ring-error/30 focus:border-error'
          : 'border-neutral-300 focus:ring-primary/30 focus:border-primary/40',
      ]"
    />
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  min: { type: [String, Number], default: undefined },
  max: { type: [String, Number], default: undefined },
  invalid: { type: Boolean, default: false },
})

defineEmits(['update:modelValue'])
</script>
