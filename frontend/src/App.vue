<template>
  <div id="app" class="min-h-screen bg-neutral-100">
    <Transition name="status-slide">
      <div
        v-if="!isOnline"
        class="fixed left-0 right-0 top-0 z-50 flex items-center justify-center gap-2 bg-amber-500 px-3 py-1.5 text-xs font-semibold text-white"
      >
        <AppIcon name="offline" size="sm" :stroke-width="2.5" class="shrink-0" />
        Sin conexion - Los registros se guardaran localmente y se sincronizaran al reconectar
        <span v-if="produccionStore.pendingCount > 0" class="ml-1 rounded bg-white/20 px-1.5">
          {{ produccionStore.pendingCount }} pendiente{{ produccionStore.pendingCount !== 1 ? 's' : '' }}
        </span>
      </div>
    </Transition>

    <template v-if="authStore.isAuthenticated">
      <div :class="['min-h-screen', !isOnline ? 'pt-8' : '']">
        <header class="sticky top-0 z-30 border-b border-neutral-200 bg-white md:hidden">
          <div class="flex h-14 items-center justify-between px-4">
            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-lg border border-neutral-200 text-neutral-700"
              aria-label="Abrir navegacion"
              @click="mobileMenuOpen = true"
            >
              <AppIcon name="menu" />
            </button>
            <div class="min-w-0 px-3 text-center">
              <p class="truncate text-sm font-extrabold text-primary-dark">Registro Produccion</p>
              <p class="truncate text-xs font-semibold text-neutral-400">{{ userRoleLabel }} - {{ isOnline ? 'En linea' : 'Sin conexion' }}</p>
            </div>
            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-lg border border-neutral-200 text-neutral-600"
              aria-label="Cerrar sesion"
              @click="handleLogout"
            >
              <AppIcon name="logout" size="sm" />
            </button>
          </div>
        </header>

        <Transition name="backdrop-fade">
          <div
            v-if="mobileMenuOpen"
            class="fixed inset-0 z-40 bg-neutral-900/45 md:hidden"
            @click="mobileMenuOpen = false"
          ></div>
        </Transition>

        <aside
          :class="[
            'fixed inset-y-0 left-0 z-50 flex w-72 max-w-[86vw] flex-col border-r border-neutral-200 bg-white shadow-xl transition-transform duration-200 md:z-20 md:translate-x-0 md:shadow-none',
            mobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
          ]"
        >
          <div class="flex h-16 shrink-0 items-center justify-between border-b border-neutral-100 px-4">
            <div class="min-w-0">
              <p class="truncate text-lg font-extrabold text-primary-dark">Registro Produccion</p>
              <p class="truncate text-xs font-semibold text-neutral-400">{{ authStore.userName }}</p>
            </div>
            <button
              type="button"
              class="flex h-9 w-9 items-center justify-center rounded-lg text-neutral-500 hover:bg-neutral-100 md:hidden"
              aria-label="Cerrar menu"
              @click="mobileMenuOpen = false"
            >
              <AppIcon name="close" size="sm" />
            </button>
          </div>

          <nav class="min-h-0 flex-1 overflow-y-auto px-3 py-4">
            <div class="space-y-2">
              <router-link
                v-for="item in primaryItems"
                :key="item.key"
                :to="item.to"
                :class="navItemClass(isItemActive(item))"
                exact-active-class="!border-primary-dark !bg-primary-dark !text-white"
                @click="mobileMenuOpen = false"
              >
                <span class="flex min-w-0 items-center gap-3">
                  <AppIcon :name="item.icon" size="sm" class="shrink-0" />
                  <span class="truncate">{{ item.label }}</span>
                </span>
              </router-link>

              <section v-for="section in navSections" :key="section.key" class="pt-2">
                <button
                  type="button"
                  :class="navSectionClass(section)"
                  @click="toggleSection(section.key)"
                >
                  <span class="flex min-w-0 items-center gap-2">
                    <span
                      :class="[
                        'h-1.5 w-1.5 rounded-full transition-colors',
                        isSectionActive(section) ? 'bg-primary-dark' : 'bg-neutral-400',
                      ]"
                    ></span>
                    <span class="truncate">{{ section.label }}</span>
                  </span>
                  <AppIcon
                    name="chevronDown"
                    size="xs"
                    :class="['shrink-0 transition-transform', openSections[section.key] ? 'rotate-180' : '']"
                  />
                </button>

                <Transition name="nav-section">
                  <div v-show="openSections[section.key]" class="mt-1 space-y-1 overflow-hidden">
                    <router-link
                      v-for="item in section.items"
                      :key="item.key"
                      :to="item.to"
                      :class="navItemClass(isItemActive(item))"
                      @click="mobileMenuOpen = false"
                    >
                      <span class="flex min-w-0 items-center gap-3">
                        <AppIcon :name="item.icon" size="sm" class="shrink-0" />
                        <span class="truncate">{{ item.label }}</span>
                      </span>
                      <span
                        v-if="Number(item.badge || 0) > 0"
                        class="ml-2 rounded-full bg-warning px-2 py-0.5 text-[10px] font-extrabold text-white"
                      >
                        {{ item.badge }}
                      </span>
                    </router-link>
                  </div>
                </Transition>
              </section>
            </div>
          </nav>

          <div class="shrink-0 border-t border-neutral-100 p-3">
            <router-link
              :to="{ name: 'configuracion' }"
              :class="navItemClass(route.name === 'configuracion')"
              @click="mobileMenuOpen = false"
            >
              <span class="flex min-w-0 items-center gap-3">
                <AppIcon name="settings" size="sm" />
                <span class="truncate">Configuracion</span>
              </span>
            </router-link>

            <div class="mt-3 rounded-lg bg-neutral-50 p-3">
              <p class="truncate text-sm font-bold text-neutral-800">{{ authStore.userName }}</p>
              <p class="mt-0.5 text-xs font-semibold text-neutral-400">{{ userRoleLabel }} - {{ isOnline ? 'En linea' : 'Sin conexion' }}</p>
              <button
                type="button"
                class="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm font-semibold text-neutral-600 hover:border-error hover:text-error"
                @click="handleLogout"
              >
                <AppIcon name="logout" size="sm" />
                Salir
              </button>
            </div>
          </div>
        </aside>

        <main class="min-h-screen md:pl-72">
          <router-view v-slot="{ Component, route: viewRoute }">
            <Transition name="route-fade" mode="out-in">
              <div :key="viewRoute.fullPath" v-motion-page class="min-h-screen">
                <component :is="Component" />
              </div>
            </Transition>
          </router-view>
        </main>
      </div>
    </template>

    <router-view v-else v-slot="{ Component, route: viewRoute }">
      <Transition name="route-fade" mode="out-in">
        <div :key="viewRoute.fullPath" v-motion-page class="min-h-screen">
          <component :is="Component" />
        </div>
      </Transition>
    </router-view>
    <ToastHost />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, provide, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import ToastHost from '@/components/ToastHost.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const produccionStore = useProduccionStore()
const mobileMenuOpen = ref(false)
const openSections = reactive({
  operacion: true,
  catalogos: true,
  produccion: true,
})

const isAdmin = computed(() => authStore.isAdmin)
const isEncargado = computed(() => authStore.user?.encargado === 1)
const canViewDashboard = computed(() => isAdmin.value || isEncargado.value)

const userRoleLabel = computed(() => {
  if (isAdmin.value) return 'Admin'
  if (isEncargado.value) return 'Encargado'
  return 'Operador'
})

const primaryItems = computed(() => [
  { key: 'home', label: 'Inicio', icon: 'home', to: { name: 'home' } },
  { key: 'manuales', label: 'Manuales', icon: 'manual', to: { name: 'manuales' } },
])

const navSections = computed(() => {
  const sections = []

  if (canViewDashboard.value || isAdmin.value) {
    const operacionItems = []
    if (canViewDashboard.value) {
      operacionItems.push({ key: 'dashboard', label: 'Dashboard Operativo', icon: 'dashboard', to: { name: 'dashboard' } })
    }
    if (isAdmin.value) {
      operacionItems.push(
        { key: 'personal', label: 'Personal', icon: 'personnel', to: { name: 'admin-crud', params: { entity: 'personal' } } },
        { key: 'moviles', label: 'Moviles', icon: 'machine', to: { name: 'admin-crud', params: { entity: 'moviles' } } },
        { key: 'asignaciones', label: 'Asignaciones Operativas', icon: 'assignment', to: { name: 'admin-crud', params: { entity: 'asignaciones' } } },
      )
    }
    sections.push({ key: 'operacion', label: 'Operacion', items: operacionItems })
  }

  if (isAdmin.value) {
    sections.push({
      key: 'catalogos',
      label: 'Catalogos',
      items: [
        { key: 'unidades', label: 'Unidades de Negocio', icon: 'unit', to: { name: 'admin-crud', params: { entity: 'unidades-negocio' } } },
        { key: 'tipos', label: 'Tipos de Proceso', icon: 'process', to: { name: 'admin-crud', params: { entity: 'tipos-proceso' } } },
        { key: 'lugares', label: 'Lugares de Carga', icon: 'location', to: { name: 'admin-crud', params: { entity: 'lugares-carga' } } },
        { key: 'predios', label: 'Predios', icon: 'field', to: { name: 'admin-crud', params: { entity: 'predios' } } },
        { key: 'rodales', label: 'Rodales', icon: 'plot', to: { name: 'admin-crud', params: { entity: 'rodales' } } },
        { key: 'acceso', label: 'Configuracion de Acceso', icon: 'settings', to: { name: 'admin-configuracion' } },
      ],
    })
  }

  const produccionItems = [
    { key: 'carga-produccion', label: 'Carga de Produccion', icon: 'production', to: { name: 'produccion' } },
    { key: 'pendientes', label: 'Pendientes', icon: 'pending', to: { name: 'pendientes' }, badge: produccionStore.pendingCount },
  ]

  if (!isEncargado.value || isAdmin.value) {
    produccionItems.push({ key: 'mis-registros', label: 'Mis Registros', icon: 'records', to: { name: 'mis-registros' } })
  }

  sections.push({ key: 'produccion', label: 'Produccion', items: produccionItems })
  return sections
})

function toggleSection(key) {
  openSections[key] = !openSections[key]
}

function navItemClass(active) {
  return [
    'flex min-h-11 items-center justify-between gap-2 rounded-lg border px-3 py-2 text-sm font-bold transition-all duration-150 ease-out hover:-translate-y-px active:translate-y-0 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20',
    active
      ? 'border-primary-dark bg-primary-dark text-white'
      : 'border-neutral-200/80 bg-white text-neutral-800 shadow-sm hover:border-primary/25 hover:bg-primary-light/20 hover:text-primary-dark hover:shadow',
  ]
}

function navSectionClass(section) {
  const active = isSectionActive(section)
  const open = openSections[section.key]

  return [
    'flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left text-xs font-extrabold uppercase tracking-wide transition-all duration-150 ease-out hover:-translate-y-px active:translate-y-0 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20',
    active
      ? 'border-primary/25 bg-primary-light/35 text-primary-dark shadow-sm'
      : open
        ? 'border-neutral-200 bg-neutral-50 text-neutral-700'
        : 'border-neutral-200/80 bg-white text-neutral-600 shadow-sm hover:border-primary/25 hover:bg-primary-light/20 hover:text-primary-dark',
  ]
}

function isSectionActive(section) {
  return section.items.some(isItemActive)
}

function isItemActive(item) {
  if (item.to.name === 'admin-crud') {
    return route.name === 'admin-crud' && route.params.entity === item.to.params.entity
  }
  return route.name === item.to.name
}

watch(
  () => route.fullPath,
  () => {
    mobileMenuOpen.value = false
  },
)

// PWA install prompt
const deferredInstallPrompt = ref(null)

function handleBeforeInstallPrompt(e) {
  e.preventDefault()
  deferredInstallPrompt.value = e
}

function handleAppInstalled() {
  deferredInstallPrompt.value = null
}

async function installApp() {
  const installPrompt = deferredInstallPrompt.value
  if (!installPrompt) return

  deferredInstallPrompt.value = null

  try {
    await installPrompt.prompt()
    const { outcome } = await installPrompt.userChoice
    if (outcome !== 'accepted') {
      return
    }
  } catch (error) {
    console.error('No se pudo mostrar el prompt de instalacion:', error)
  }
}

provide('pwaInstall', { deferredInstallPrompt, installApp })

// Offline / sync management
const isOnline = ref(navigator.onLine)
const SYNC_INTERVAL_MS = 5 * 60 * 1000
let syncIntervalId = null

async function handleOnline() {
  isOnline.value = true
  if (navigator.onLine && authStore.isAuthenticated) {
    await produccionStore.syncPending()
  }
}

function handleOffline() {
  isOnline.value = false
}

onMounted(() => {
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.addEventListener('appinstalled', handleAppInstalled)
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
  if (authStore.isAuthenticated) {
    produccionStore.refreshPendingCount()
  }

  syncIntervalId = setInterval(async () => {
    if (navigator.onLine && authStore.isAuthenticated) {
      await produccionStore.syncPending()
    }
  }, SYNC_INTERVAL_MS)
})

onUnmounted(() => {
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.removeEventListener('appinstalled', handleAppInstalled)
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
  if (syncIntervalId) clearInterval(syncIntervalId)
})

function handleLogout() {
  authStore.logout()
  mobileMenuOpen.value = false
  router.push({ name: 'login' })
}
</script>
