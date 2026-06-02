<template>
  <div class="relative">
    <label v-if="label" class="block text-sm font-medium text-neutral-700 mb-1">
      {{ label }}
    </label>

    <!-- ── Selected state (like machine assignment) ── -->
    <button
      v-if="selectedLabel && !searching && selectedDisplay === 'input'"
      type="button"
      :disabled="disabled"
      @click="startSearch"
      class="flex w-full items-center justify-between gap-3 rounded-xl border border-neutral-300 bg-neutral-50 px-4 py-3 text-left text-sm font-semibold text-neutral-900 transition-colors hover:bg-white disabled:cursor-not-allowed disabled:bg-neutral-200"
    >
      <span class="min-w-0 truncate">{{ selectedLabel }}</span>
      <AppIcon name="chevronDown" size="sm" class="shrink-0 text-neutral-500" />
    </button>

    <div
      v-else-if="selectedLabel && !searching"
      class="flex items-center gap-3 p-3 bg-success-light/40 border border-success/30 rounded-xl"
    >
      <AppIcon name="success" class="text-success-dark shrink-0" />
      <span class="text-sm font-semibold text-neutral-900 min-w-0 flex-1 truncate">{{ selectedLabel }}</span>
      <button
        v-if="!disabled"
        type="button"
        @click="startSearch"
        class="shrink-0 text-xs font-medium text-primary hover:text-primary-dark underline underline-offset-2"
      >
        Cambiar
      </button>
    </div>

    <!-- ── Search state ── -->
    <div v-else>
      <div class="relative">
        <input
          ref="inputRef"
          :id="inputId"
          type="text"
          v-model="query"
          @focus="isOpen = true"
          @blur="onBlur"
          @input="onInput"
          @keydown.escape="cancelSearch"
          @keydown.enter.prevent="selectHighlighted"
          @keydown.arrow-down.prevent="moveDown"
          @keydown.arrow-up.prevent="moveUp"
          :placeholder="placeholder"
          :disabled="disabled"
          role="combobox"
          autocomplete="off"
          :aria-expanded="isOpen"
          :aria-controls="listboxId"
          :aria-activedescendant="activeDescendantId"
          :aria-invalid="invalid || undefined"
          :class="[
            'w-full px-4 py-3 bg-neutral-100 border rounded-xl text-neutral-900 placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:border-primary/40 disabled:bg-neutral-200 disabled:cursor-not-allowed transition-colors',
            invalid
              ? 'border-error focus:ring-error/30 focus:border-error'
              : 'border-neutral-300 focus:ring-primary/30 focus:border-primary/40',
          ]"
        />
        <button
          v-if="query"
          type="button"
          @mousedown.prevent="query = ''; isOpen = true"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
          tabindex="-1"
        >
          <AppIcon name="close" size="sm" />
        </button>
      </div>

      <!-- Inline results list (no absolute — expands card naturally) -->
      <div
        v-if="isOpen && filteredItems.length > 0"
        :id="listboxId"
        role="listbox"
        class="absolute left-0 right-0 top-full z-50 mt-1.5 max-h-56 overflow-y-auto rounded-xl border border-neutral-200 bg-white shadow-xl"
      >
        <button
          v-for="(item, i) in filteredItems"
          :key="getKey(item)"
          :id="optionId(i)"
          type="button"
          role="option"
          :aria-selected="i === highlightedIndex"
          @mousedown.prevent="selectItem(item)"
          :class="[
            'w-full text-left px-4 py-2.5 border-b last:border-b-0 border-neutral-100 transition-colors text-sm',
            i === highlightedIndex
              ? 'bg-primary/10 text-primary-dark font-medium'
              : 'hover:bg-neutral-50 text-neutral-900',
          ]"
        >
          {{ getLabel(item) }}
        </button>
      </div>

      <!-- No results -->
      <div
        v-else-if="isOpen && query.length >= 1 && filteredItems.length === 0"
        class="absolute left-0 right-0 top-full z-50 mt-1.5 rounded-lg border border-neutral-200 bg-white p-2.5 text-xs text-neutral-400 shadow-xl"
      >
        Sin resultados para "{{ query }}"
      </div>

      <!-- Cancel (only when switching from an already-selected value) -->
      <button
        v-if="modelValue && searching"
        type="button"
        @click="cancelSearch"
        class="mt-2 text-xs text-neutral-400 hover:text-neutral-600 underline underline-offset-2 block"
      >
        Cancelar
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps({
  modelValue: { type: [String, Number, null], default: null },
  items: { type: Array, default: () => [] },
  labelKey: { type: String, default: 'label' },
  valueKey: { type: String, default: 'id' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '— Escribí para buscar —' },
  disabled: { type: Boolean, default: false },
  invalid: { type: Boolean, default: false },
  selectedDisplay: { type: String, default: 'chip' },
})

const emit = defineEmits(['update:modelValue', 'select'])

const query = ref('')
const isOpen = ref(false)
const searching = ref(false)   // true when in active-search mode (even if value exists)
const highlightedIndex = ref(-1)
const inputRef = ref(null)
const uniqueId = Math.random().toString(36).slice(2)
const inputId = `autocomplete-input-${uniqueId}`
const listboxId = `autocomplete-listbox-${uniqueId}`
const activeDescendantId = computed(() => highlightedIndex.value >= 0 ? optionId(highlightedIndex.value) : undefined)

const selectedLabel = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '' || props.modelValue === 0) return ''
  const found = props.items.find(item => String(getKey(item)) === String(props.modelValue))
  return found ? getLabel(found) : ''
})

function getLabel(item) {
  return typeof item === 'object' ? item[props.labelKey] ?? '' : String(item)
}

function getKey(item) {
  return typeof item === 'object' ? item[props.valueKey] : item
}

function optionId(index) {
  return `autocomplete-option-${uniqueId}-${index}`
}

const filteredItems = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return props.items.slice(0, 15)
  return props.items
    .filter(item => getLabel(item).toLowerCase().includes(q))
    .slice(0, 15)
})

function startSearch() {
  searching.value = true
  query.value = ''
  isOpen.value = true
  nextTick(() => inputRef.value?.focus())
}

function cancelSearch() {
  searching.value = false
  isOpen.value = false
  query.value = ''
}

function onBlur() {
  setTimeout(() => {
    isOpen.value = false
    if (!props.modelValue) searching.value = false
  }, 200)
}

function onInput() {
  isOpen.value = true
  highlightedIndex.value = -1
}

function selectItem(item) {
  emit('update:modelValue', getKey(item))
  emit('select', item)
  query.value = ''
  isOpen.value = false
  searching.value = false
  highlightedIndex.value = -1
}

function selectHighlighted() {
  if (highlightedIndex.value >= 0 && filteredItems.value[highlightedIndex.value]) {
    selectItem(filteredItems.value[highlightedIndex.value])
  }
}

function moveDown() {
  if (!isOpen.value) { isOpen.value = true; return }
  highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredItems.value.length - 1)
}

function moveUp() {
  highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
}

// When modelValue changes externally (e.g. reset), go back to selected state
watch(() => props.modelValue, (val) => {
  if (!val && val !== 0) {
    searching.value = false
    query.value = ''
    isOpen.value = false
  }
})
</script>
