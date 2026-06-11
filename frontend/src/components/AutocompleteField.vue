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
      class="app-input flex w-full items-center justify-between gap-3 rounded-xl border px-4 py-2.5 text-left text-sm font-semibold transition-all duration-150 ease-out hover:-translate-y-px hover:bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20 active:translate-y-0 active:scale-[0.99] disabled:cursor-not-allowed disabled:bg-neutral-200"
    >
      <span class="min-w-0 truncate">{{ selectedLabel }}</span>
      <AppIcon name="chevronDown" size="sm" class="shrink-0 text-neutral-500" />
    </button>

    <div
      v-else-if="selectedLabel && !searching"
      v-motion-pop
      class="flex items-center gap-3 rounded-xl border border-success/30 bg-success-light/40 p-2.5"
    >
      <AppIcon name="success" class="text-success-dark shrink-0" />
      <span class="text-sm font-semibold text-neutral-900 min-w-0 flex-1 truncate">{{ selectedLabel }}</span>
      <button
        v-if="!disabled"
        type="button"
        @click="startSearch"
        class="shrink-0 text-xs font-medium text-info hover:text-info-dark underline underline-offset-2"
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
            'app-input w-full rounded-xl border px-4 py-2.5 placeholder:text-neutral-400 focus:border-primary/40 focus:outline-none focus:ring-2 disabled:cursor-not-allowed disabled:bg-neutral-200 transition-colors',
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
      <Transition name="dropdown-soft">
        <div
          v-if="isOpen && filteredItems.length > 0"
          :id="listboxId"
          role="listbox"
          :class="resultsListClass"
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
              'w-full border-b border-neutral-100 px-4 py-2 text-left text-sm transition-colors last:border-b-0',
              i === highlightedIndex
                ? 'bg-info-light text-info-dark font-medium'
                : 'hover:bg-neutral-50 text-neutral-900',
            ]"
          >
            {{ getLabel(item) }}
          </button>
        </div>
      </Transition>

      <!-- No results -->
      <Transition name="dropdown-soft">
        <div
          v-if="isOpen && query.length >= 1 && filteredItems.length === 0"
          :class="emptyListClass"
        >
          Sin resultados para "{{ query }}"
        </div>
      </Transition>

      <!-- Cancel (only when switching from an already-selected value) -->
      <Transition name="fade-soft">
        <button
          v-if="modelValue && searching"
          type="button"
          @click="cancelSearch"
          class="mt-2 block text-xs text-neutral-400 underline underline-offset-2 transition-colors hover:text-neutral-600"
        >
          Cancelar
        </button>
      </Transition>
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
  dropdownMode: { type: String, default: 'absolute' },
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
const usesInlineDropdown = computed(() => props.dropdownMode === 'inline')
const resultsListClass = computed(() => [
  'app-card z-50 mt-1.5 max-h-56 overflow-y-auto rounded-xl',
  usesInlineDropdown.value ? 'relative' : 'absolute left-0 right-0 top-full',
])
const emptyListClass = computed(() => [
  'app-card z-50 mt-1.5 rounded-lg p-2.5 text-xs text-neutral-400',
  usesInlineDropdown.value ? 'relative' : 'absolute left-0 right-0 top-full',
])

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
