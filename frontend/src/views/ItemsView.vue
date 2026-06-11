<template>
  <div class="min-h-screen bg-neutral-100 px-3 py-3 pb-20 md:px-4 md:py-4">
    <div class="mx-auto max-w-6xl space-y-3">
      <PageHeader title="Items" description="Catalogo operativo disponible para produccion.">
        <template #actions>
          <AppButton variant="secondary" :loading="loading" @click="fetchItems">
            <AppIcon name="refresh" size="sm" />
            Refrescar
          </AppButton>
        </template>
      </PageHeader>

      <section class="app-card rounded-xl p-4">
        <div v-if="loading" class="py-4 text-center text-sm text-neutral-500">Cargando items...</div>
        <div v-else-if="error" class="rounded-lg border border-error/25 bg-error-light/30 p-3 text-sm font-semibold text-error-dark">
          Error: {{ error }}
        </div>
        <EmptyState v-else-if="items.length === 0" title="Sin items" description="No hay items disponibles para mostrar." />
        <ul v-else class="divide-y divide-neutral-100">
          <li v-for="item in items" :key="item.id" class="grid gap-1 py-2.5 sm:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
            <span class="truncate text-sm font-extrabold text-neutral-900">{{ item.name }}</span>
            <span class="truncate text-sm text-neutral-500">{{ item.description || '-' }}</span>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useItemsStore } from '@/stores/items'
import { onMounted } from 'vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import PageHeader from '@/components/ui/PageHeader.vue'

const itemsStore = useItemsStore()
const { items, loading, error } = storeToRefs(itemsStore)
const { fetchItems } = itemsStore

onMounted(() => {
  fetchItems()
})
</script>
