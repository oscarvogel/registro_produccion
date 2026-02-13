<template>
  <div>
    <label v-if="label" class="block text-sm font-medium text-neutral-700 mb-1">
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
      class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
             placeholder:text-neutral-400
             focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
             disabled:bg-neutral-100 disabled:cursor-not-allowed
             transition-colors"
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
})

defineEmits(['update:modelValue'])
</script>
