<template>
  <div class="space-y-3">
    <PageHeader
      kicker="Administración"
      title="Centro administrativo"
      description="Gestioná personas, equipos, catálogos y accesos desde un único lugar."
      elevated
    />

    <section class="grid gap-3 lg:grid-cols-2 xl:grid-cols-3" aria-label="Áreas administrativas">
      <article
        v-for="group in adminGroups"
        :key="group.key"
        class="app-card flex min-h-full flex-col rounded-xl p-4"
      >
        <header class="mb-3 flex items-start gap-3 border-b border-neutral-200 pb-3">
          <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-light/35 text-primary-dark">
            <AppIcon :name="group.icon" />
          </span>
          <div class="min-w-0">
            <h2 class="text-lg font-extrabold text-neutral-950">{{ group.title }}</h2>
            <p class="mt-1 text-sm text-neutral-500">{{ group.description }}</p>
          </div>
        </header>

        <nav class="grid gap-2" :aria-label="group.title">
          <router-link
            v-for="item in group.items"
            :key="item.key"
            :to="item.to"
            class="app-surface-muted group flex min-h-12 items-center justify-between gap-3 rounded-lg border px-3 py-2.5 text-left transition hover:-translate-y-px hover:border-primary/35 hover:bg-primary-light/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30"
          >
            <span class="flex min-w-0 items-center gap-3">
              <AppIcon :name="item.icon" size="sm" class="shrink-0 text-neutral-500 group-hover:text-primary-dark" />
              <span class="min-w-0">
                <span class="block text-sm font-extrabold text-neutral-900">{{ item.label }}</span>
                <span class="mt-0.5 block text-xs text-neutral-500">{{ item.description }}</span>
              </span>
            </span>
            <AppIcon name="forward" size="sm" class="shrink-0 text-neutral-400 group-hover:text-primary-dark" />
          </router-link>
        </nav>
      </article>
    </section>
  </div>
</template>

<script setup>
import AppIcon from '@/components/ui/AppIcon.vue'
import PageHeader from '@/components/ui/PageHeader.vue'

const adminGroups = [
  {
    key: 'personas-equipos',
    title: 'Personas y equipos',
    description: 'Personal, móviles y asignaciones operativas.',
    icon: 'personnel',
    items: [
      { key: 'personal', label: 'Personal', description: 'Usuarios, roles y relaciones operativas.', icon: 'personnel', to: { name: 'admin-crud', params: { entity: 'personal' } } },
      { key: 'moviles', label: 'Móviles', description: 'Equipos, unidades y datos técnicos.', icon: 'machine', to: { name: 'admin-crud', params: { entity: 'moviles' } } },
      { key: 'asignaciones', label: 'Asignaciones operativas', description: 'Choferes, móviles y procesos vinculados.', icon: 'assignment', to: { name: 'admin-crud', params: { entity: 'asignaciones' } } },
    ],
  },
  {
    key: 'configuracion-productiva',
    title: 'Configuración productiva',
    description: 'Catálogos utilizados durante las cargas.',
    icon: 'process',
    items: [
      { key: 'unidades', label: 'Unidades de negocio', description: 'Estructura operativa y vinculaciones.', icon: 'unit', to: { name: 'admin-crud', params: { entity: 'unidades-negocio' } } },
      { key: 'procesos', label: 'Tipos de proceso', description: 'Procesos y requisitos de carga.', icon: 'process', to: { name: 'admin-crud', params: { entity: 'tipos-proceso' } } },
      { key: 'lugares', label: 'Lugares de carga', description: 'Puntos de carga por unidad.', icon: 'location', to: { name: 'admin-crud', params: { entity: 'lugares-carga' } } },
      { key: 'predios', label: 'Predios', description: 'Predios disponibles para producción.', icon: 'field', to: { name: 'admin-crud', params: { entity: 'predios' } } },
      { key: 'rodales', label: 'Rodales', description: 'Rodales y valores productivos.', icon: 'plot', to: { name: 'admin-crud', params: { entity: 'rodales' } } },
      { key: 'actas', label: 'Actas', description: 'Actas habilitadas para registrar producción.', icon: 'records', to: { name: 'admin-crud', params: { entity: 'actas' } } },
    ],
  },
  {
    key: 'seguridad',
    title: 'Seguridad',
    description: 'Permisos generales y políticas de acceso.',
    icon: 'admin',
    items: [
      { key: 'acceso', label: 'Configuración de acceso', description: 'Parámetros administrativos y de seguridad.', icon: 'settings', to: { name: 'admin-configuracion' } },
    ],
  },
]
</script>
