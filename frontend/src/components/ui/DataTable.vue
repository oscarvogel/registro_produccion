<template>
  <div class="app-table overflow-x-auto rounded-xl">
    <table class="min-w-full text-sm">
      <thead class="app-table-head sticky top-0 z-10">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            class="whitespace-nowrap border-b border-neutral-200 px-3 py-2 text-left font-semibold"
          >
            <button
              v-if="column.sortable"
              class="inline-flex items-center gap-1 hover:text-info-dark"
              type="button"
              @click="toggleSort(column.key)"
            >
              {{ column.label }}
              <span class="text-[10px] font-extrabold text-primary-dark">{{ sortIndicator(column.key) }}</span>
            </button>
            <span v-else>{{ column.label }}</span>
          </th>
          <th v-if="$slots.actions" class="border-b border-neutral-200 px-3 py-2 text-right font-semibold">Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="px-3 py-5 text-center text-neutral-500">Cargando...</td>
        </tr>
        <tr v-else-if="sortedRows.length === 0">
          <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="px-3 py-5 text-center text-neutral-500">{{ emptyText }}</td>
        </tr>
        <tr v-for="row in sortedRows" :key="row[rowKey]" class="app-table-row">
          <td v-for="column in columns" :key="`${row[rowKey]}-${column.key}`" class="border-b border-neutral-100 px-3 py-2">
            <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
              {{ row[column.key] ?? '-' }}
            </slot>
          </td>
          <td v-if="$slots.actions" class="border-b border-neutral-100 px-3 py-2 text-right">
            <slot name="actions" :row="row" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  rows: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  rowKey: { type: String, default: 'id' },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Sin registros.' },
})

const sortKey = ref('')
const sortDir = ref('asc')

const sortedRows = computed(() => {
  if (!sortKey.value) return props.rows
  return [...props.rows].sort((a, b) => {
    const left = String(a[sortKey.value] ?? '').toLowerCase()
    const right = String(b[sortKey.value] ?? '').toLowerCase()
    const result = left.localeCompare(right)
    return sortDir.value === 'asc' ? result : -result
  })
})

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function sortIndicator(key) {
  if (sortKey.value !== key) return ''
  return sortDir.value === 'asc' ? 'ASC' : 'DESC'
}
</script>
