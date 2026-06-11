<template>
  <div class="app-card rounded-xl p-4">
    <div class="flex flex-col gap-3 lg:flex-row lg:items-end">
      <AutocompleteField
        :model-value="modelValue.unidad_id"
        class="w-full lg:w-64"
        label="Unidad de Negocio"
        :items="unidadOptions"
        labelKey="_adminLabel"
        valueKey="idUnidadNegocio"
        placeholder="Buscar unidad"
        @update:model-value="updateField('unidad_id', $event)"
      />

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 flex-1">
        <AutocompleteField
          :model-value="modelValue.idChofer"
          label="Chofer"
          :items="assignmentOptions.personal"
          labelKey="_adminLabel"
          valueKey="idPersonal"
          :disabled="!modelValue.unidad_id"
          placeholder="Buscar chofer"
          @update:model-value="updateField('idChofer', $event)"
        />
        <AutocompleteField
          :model-value="modelValue.idMovil"
          label="Movil"
          :items="assignmentOptions.moviles"
          labelKey="_adminLabel"
          valueKey="idMovil"
          :disabled="!modelValue.unidad_id"
          placeholder="Buscar movil"
          @update:model-value="updateField('idMovil', $event)"
        />
        <AutocompleteField
          :model-value="modelValue.idProceso"
          label="Tipo de Proceso"
          :items="assignmentOptions.procesos"
          labelKey="_adminLabel"
          valueKey="id"
          :disabled="!modelValue.unidad_id"
          placeholder="Buscar proceso"
          @update:model-value="updateField('idProceso', $event)"
        />
      </div>

      <button
        @click="$emit('submit')"
        :disabled="submitting || !ready"
        class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-primary-dark text-white text-sm font-semibold disabled:opacity-50"
        type="button"
      >
        <AppIcon name="assignment" size="sm" />
        Asignar
      </button>
    </div>
  </div>
</template>

<script setup>
import AutocompleteField from '@/components/AutocompleteField.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  unidadOptions: { type: Array, required: true },
  assignmentOptions: { type: Object, required: true },
  ready: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit'])

function updateField(key, value) {
  emit('update:modelValue', {
    ...props.modelValue,
    [key]: value,
  })
}
</script>
