<template>
  <div class="min-h-[calc(100vh-8.5rem)] bg-neutral-100 px-4 py-5 md:min-h-[calc(100vh-3.5rem)] md:py-6">
    <div class="mx-auto max-w-7xl space-y-4">
      <header class="rounded-2xl border border-neutral-200 bg-white px-5 py-4 shadow-sm">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Panel de Administracion</p>
            <h1 class="text-xl font-extrabold text-primary-dark md:text-2xl">Centro de control del sistema</h1>
            <p class="mt-1 text-sm text-neutral-500">Controla usuarios, unidades de negocio, permisos y metricas operativas.</p>
          </div>
          <p class="text-xs font-semibold text-neutral-400">Gestion - Catalogos - Dashboard operativo</p>
        </div>
      </header>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-[17rem_1fr]">
        <aside class="h-fit md:sticky md:top-16">
          <nav class="rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm">
            <div class="mb-4">
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Gestion del sistema</p>
              <h2 class="mt-1 text-lg font-extrabold text-primary-dark">Modulos Admin</h2>
            </div>

            <div class="space-y-5">
              <div v-for="group in navGroups" :key="group.title">
                <p class="mb-2 px-1 text-[11px] font-bold uppercase tracking-wide text-neutral-400">{{ group.title }}</p>
                <div class="space-y-1.5">
                  <router-link
                    v-for="item in group.items"
                    :key="item.key"
                    :to="item.to"
                    :class="[
                      'flex items-center justify-between rounded-lg border px-3 py-2 text-sm font-semibold transition-colors',
                      isActive(item)
                        ? 'border-primary-dark bg-primary-dark text-white'
                        : 'border-neutral-200 bg-neutral-50 text-neutral-700 hover:border-primary/30 hover:bg-white hover:text-primary-dark',
                    ]"
                  >
                    <span class="flex min-w-0 items-center gap-2">
                      <AppIcon :name="item.icon" size="sm" class="shrink-0" />
                      <span class="truncate">{{ item.label }}</span>
                    </span>
                    <AppIcon name="chevronDown" size="xs" class="-rotate-90 opacity-80" />
                  </router-link>
                </div>
              </div>
            </div>
          </nav>
        </aside>

        <section class="min-w-0">
          <router-view />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppIcon from '@/components/ui/AppIcon.vue'

const route = useRoute()

const navGroups = [
  {
    title: 'Operacion',
    items: [
      { key: 'dashboard', label: 'Dashboard operativo', icon: 'dashboard', to: { name: 'admin-dashboard' } },
      { key: 'personal', label: 'Personal', icon: 'personnel', to: { name: 'admin-crud', params: { entity: 'personal' } } },
      { key: 'moviles', label: 'Moviles', icon: 'machine', to: { name: 'admin-crud', params: { entity: 'moviles' } } },
      { key: 'asignaciones', label: 'Asignaciones Operativas', icon: 'assignment', to: { name: 'admin-crud', params: { entity: 'asignaciones' } } },
    ],
  },
  {
    title: 'Catalogos',
    items: [
      { key: 'unidades', label: 'Unidades de Negocio', icon: 'unit', to: { name: 'admin-crud', params: { entity: 'unidades-negocio' } } },
      { key: 'tipos', label: 'Tipos de Proceso', icon: 'process', to: { name: 'admin-crud', params: { entity: 'tipos-proceso' } } },
      { key: 'lugares', label: 'Lugares de Carga', icon: 'location', to: { name: 'admin-crud', params: { entity: 'lugares-carga' } } },
      { key: 'predios', label: 'Predios', icon: 'field', to: { name: 'admin-crud', params: { entity: 'predios' } } },
      { key: 'rodales', label: 'Rodales', icon: 'plot', to: { name: 'admin-crud', params: { entity: 'rodales' } } },
    ],
  },
  {
    title: 'Sistema',
    items: [
      { key: 'config', label: 'Configuracion de Acceso', icon: 'settings', to: { name: 'admin-configuracion' } },
    ],
  },
]

function isActive(item) {
  if (item.to.name === 'admin-crud') {
    return route.name === 'admin-crud' && route.params.entity === item.to.params.entity
  }
  return route.name === item.to.name
}
</script>
