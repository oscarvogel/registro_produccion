<template>
  <div>
    <label v-if="label" class="block text-sm font-medium text-neutral-700 mb-1">
      {{ label }}
    </label>

    <!-- ── Selected state (like machine assignment) ── -->
    <div
      v-if="selectedLabel && !searching"
      class="flex items-center gap-3 p-3 bg-success-light/40 border border-success/30 rounded-xl"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-success-dark shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
      </svg>
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
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Inline results list (no absolute — expands card naturally) -->
      <div
        v-if="isOpen && filteredItems.length > 0"
        :id="listboxId"
        role="listbox"
        class="mt-1.5 border border-neutral-200 rounded-xl bg-white max-h-52 overflow-y-auto shadow-sm"
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
        class="mt-1.5 p-2.5 text-xs text-neutral-400 bg-neutral-50 rounded-lg border border-neutral-200"
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

const props = defineProps({
  modelValue: { type: [String, Number, null], default: null },
  items: { type: Array, default: () => [] },
  labelKey: { type: String, default: 'label' },
  valueKey: { type: String, default: 'id' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '— Escribí para buscar —' },
  disabled: { type: Boolean, default: false },
  invalid: { type: Boolean, default: false },
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
  const found = props.items.find(item => getKey(item) === props.modelValue)
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
