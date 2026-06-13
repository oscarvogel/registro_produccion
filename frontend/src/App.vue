<template>
  <div id="app" class="app-shell min-h-screen">
    <Transition name="status-slide">
      <div
        v-if="!isOnline"
        class="fixed left-0 right-0 top-0 z-50 flex items-center justify-center gap-2 bg-amber-500 px-3 py-1.5 text-xs font-semibold text-white"
      >
        <AppIcon name="offline" size="sm" :stroke-width="2.5" class="shrink-0" />
        Sin conexión - Los registros se guardarán localmente y se sincronizarán al reconectar
        <span v-if="produccionStore.pendingCount > 0" class="ml-1 rounded bg-white/20 px-1.5">
          {{ produccionStore.pendingCount }} pendiente{{ produccionStore.pendingCount !== 1 ? 's' : '' }}
        </span>
      </div>
    </Transition>

    <template v-if="authStore.isAuthenticated">
      <div :class="['min-h-screen', !isOnline ? 'pt-8' : '']">
        <header class="sticky top-0 z-30 border-b border-[#222D26] bg-[#090E0B] text-white md:hidden">
          <div class="flex h-14 items-center justify-between px-4">
            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-lg border border-white/10 text-white"
              aria-label="Abrir navegacion"
              @click="mobileMenuOpen = true"
            >
              <AppIcon name="menu" />
            </button>
            <div class="min-w-0 px-3 text-center">
              <p class="truncate text-sm font-extrabold text-white">Registro Producción</p>
              <p class="truncate text-xs font-semibold text-[#9FE1CB]">{{ userRoleLabel }} - {{ isOnline ? 'En línea' : 'Sin conexión' }}</p>
            </div>
            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-lg border border-white/10 text-white/80"
              aria-label="Cerrar sesión"
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
            'fixed inset-y-0 left-0 z-50 flex w-72 max-w-[86vw] flex-col border-r border-[#222D26] bg-[#07100C] text-white shadow-xl transition-[transform,width] duration-200 md:z-20 md:max-w-none md:translate-x-0 md:shadow-none',
            sidebarCollapsed ? 'md:w-20' : 'md:w-64',
            mobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
          ]"
        >
          <div :class="['flex h-[58px] shrink-0 items-center border-b border-[#222D26] bg-[#090E0B] px-3', sidebarCollapsed ? 'md:justify-center md:px-3' : 'justify-between']">
            <div :class="['flex min-w-0 items-center gap-3', sidebarCollapsed ? 'md:hidden' : '']">
              <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#10B981] p-1 shadow-[0_0_18px_rgba(16,185,129,0.28)] ring-1 ring-[#6FFBBE]/25">
                <img src="/logo-forestal.png" alt="" class="h-full w-full object-contain" />
              </span>
              <span class="min-w-0">
                <p class="truncate text-sm font-extrabold leading-tight text-white">Registro</p>
                <p class="truncate text-xs font-bold leading-tight text-[#6FFBBE]">Producción</p>
              </span>
            </div>
            <button
              type="button"
              class="hidden h-9 w-9 items-center justify-center rounded-lg text-white/75 hover:bg-white/10 hover:text-white md:flex"
              :aria-label="sidebarCollapsed ? 'Expandir navegacion' : 'Contraer navegacion'"
              @click="toggleSidebar"
            >
              <AppIcon name="menu" size="sm" />
            </button>
            <button
              type="button"
              class="flex h-9 w-9 items-center justify-center rounded-lg text-white/75 hover:bg-white/10 md:hidden"
              aria-label="Cerrar menu"
              @click="mobileMenuOpen = false"
            >
              <AppIcon name="close" size="sm" />
            </button>
          </div>

          <div :class="['border-b border-[#222D26] px-3 py-3', sidebarCollapsed ? 'md:hidden' : '']">
            <div class="flex items-center gap-3">
              <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#115340] text-sm font-extrabold text-[#B1F0D6] ring-1 ring-[#10B981]/35">
                {{ userInitials }}
              </span>
              <div class="min-w-0">
                <p class="truncate text-sm font-extrabold uppercase text-white">{{ authStore.userName }}</p>
                <p class="flex items-center gap-1.5 text-xs font-medium text-white">
                  <span class="app-led h-1.5 w-1.5 rounded-full bg-[#10B981] text-[#10B981]"></span>
                  {{ userRoleLabel }} - {{ isOnline ? 'En línea' : 'Sin conexión' }}
                </p>
              </div>
            </div>
          </div>

          <nav :class="['min-h-0 flex-1 overflow-y-auto py-3', sidebarCollapsed ? 'md:px-2 px-2' : 'px-2']">
            <div :class="sidebarCollapsed ? 'space-y-1.5' : 'space-y-2'">
              <router-link
                v-for="item in primaryItems"
                :key="item.key"
                :to="item.to"
                :class="navItemClass(isItemActive(item))"
                :title="sidebarCollapsed ? item.label : undefined"
                exact-active-class="!border-[#10B981]/45 !bg-[#0F2A1E] !text-white"
                @click="mobileMenuOpen = false"
              >
                <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
                  <AppIcon :name="item.icon" size="sm" class="shrink-0" />
                  <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">{{ item.label }}</span>
                </span>
              </router-link>

              <section v-for="section in navSections" :key="section.key" :class="sidebarCollapsed ? 'pt-2' : 'pt-2'">
                <button
                  type="button"
                  :class="navSectionClass(section)"
                  :title="sidebarCollapsed ? section.label : undefined"
                  @click="toggleSection(section.key)"
                >
                  <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-2' : 'gap-2']">
                    <span
                      :class="[
                        'rounded-full transition-colors',
                        sidebarCollapsed ? 'md:h-2 md:w-2 h-1.5 w-1.5' : 'h-1.5 w-1.5',
                        isSectionActive(section) ? 'bg-[#10B981]' : 'bg-[#86948A]',
                      ]"
                    ></span>
                    <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">{{ section.label }}</span>
                  </span>
                  <AppIcon
                    name="chevronDown"
                    size="xs"
                    :class="['shrink-0 transition-transform', sidebarCollapsed ? 'md:hidden' : '', openSections[section.key] ? 'rotate-180' : '']"
                  />
                </button>

                <Transition name="nav-section">
                  <div v-show="sidebarCollapsed || openSections[section.key]" class="mt-1 space-y-1 overflow-hidden">
                    <router-link
                      v-for="item in section.items"
                      :key="item.key"
                      :to="item.to"
                      :class="navItemClass(isItemActive(item))"
                      :title="sidebarCollapsed ? item.label : undefined"
                      @click="mobileMenuOpen = false"
                    >
                      <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
                        <AppIcon :name="item.icon" size="sm" class="shrink-0" />
                        <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">{{ item.label }}</span>
                      </span>
                      <span
                        v-if="Number(item.badge || 0) > 0"
                        :class="[
                          'rounded-full bg-warning text-[10px] font-extrabold text-white',
                          sidebarCollapsed ? 'md:absolute md:right-2 md:top-2 md:h-2 md:w-2 md:px-0 md:py-0 md:text-transparent ml-2 px-2 py-0.5' : 'ml-2 px-2 py-0.5',
                        ]"
                      >
                        {{ item.badge }}
                      </span>
                    </router-link>
                  </div>
                </Transition>
              </section>
            </div>
          </nav>

          <div :class="['shrink-0 border-t border-[#222D26] p-2', sidebarCollapsed ? 'md:px-2' : '']">
            <button
              type="button"
              :class="navItemClass(false)"
              :title="sidebarCollapsed ? themeStatusLabel : undefined"
              :aria-label="themeToggleLabel"
              @click="toggleTheme"
            >
              <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
                <span class="relative flex h-5 w-5 shrink-0 items-center justify-center">
                  <AppIcon :name="isDark ? 'moon' : 'sun'" size="sm" class="transition-transform duration-200 group-active:scale-90" />
                </span>
                <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">{{ themeStatusLabel }}</span>
              </span>
              <span
                :class="[
                  'ml-2 h-5 w-9 rounded-full border border-white/10 p-0.5 transition-colors',
                  isDark ? 'bg-white/[0.06]' : 'bg-secondary-light/80',
                  sidebarCollapsed ? 'md:hidden' : '',
                ]"
              >
                <span
                  :class="[
                    'block h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200',
                    isDark ? 'translate-x-0' : 'translate-x-4',
                  ]"
                ></span>
              </span>
            </button>

            <router-link
              :to="{ name: 'configuracion' }"
              :class="navItemClass(route.name === 'configuracion')"
              :title="sidebarCollapsed ? 'Configuración' : undefined"
              @click="mobileMenuOpen = false"
            >
              <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
                <AppIcon name="settings" size="sm" />
                <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">Configuración</span>
              </span>
            </router-link>

            <button
              type="button"
              :class="navItemClass(false)"
              :title="sidebarCollapsed ? 'Salir' : undefined"
              @click="handleLogout"
            >
              <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
                <AppIcon name="logout" size="sm" />
                <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">Salir</span>
              </span>
            </button>
          </div>
        </aside>

        <main :class="['min-h-screen transition-[padding] duration-200', sidebarCollapsed ? 'md:pl-20' : 'md:pl-64']">
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
import { useTheme } from '@/composables/useTheme'
import ToastHost from '@/components/ToastHost.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const produccionStore = useProduccionStore()
const { isDark, toggleTheme } = useTheme()
const mobileMenuOpen = ref(false)
const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === '1')
const openSections = reactive({
  operacion: false,
  catalogos: false,
  combustible: false,
  produccion: false,
})

const isAdmin = computed(() => authStore.isAdmin)
const isEncargado = computed(() => authStore.user?.encargado === 1)
const canViewDashboard = computed(() => isAdmin.value || isEncargado.value)

const userRoleLabel = computed(() => {
  if (isAdmin.value) return 'Admin'
  if (isEncargado.value) return 'Encargado'
  return 'Operador'
})

const userInitials = computed(() => {
  const name = authStore.userName || ''
  const parts = name.trim().split(/\s+/).filter(Boolean)
  return (parts[0]?.[0] || 'U') + (parts[1]?.[0] || '')
})

const themeToggleLabel = computed(() => (isDark.value ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'))
const themeStatusLabel = computed(() => (isDark.value ? 'Modo oscuro' : 'Modo claro'))

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
        { key: 'admin-dashboard', label: 'Dashboard Producción', icon: 'dashboard', to: { name: 'admin-dashboard' } },
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
      label: 'Catálogos',
      items: [
        { key: 'unidades', label: 'Unidades de Negocio', icon: 'unit', to: { name: 'admin-crud', params: { entity: 'unidades-negocio' } } },
        { key: 'tipos', label: 'Tipos de Proceso', icon: 'process', to: { name: 'admin-crud', params: { entity: 'tipos-proceso' } } },
        { key: 'lugares', label: 'Lugares de Carga', icon: 'location', to: { name: 'admin-crud', params: { entity: 'lugares-carga' } } },
        { key: 'predios', label: 'Predios', icon: 'field', to: { name: 'admin-crud', params: { entity: 'predios' } } },
        { key: 'rodales', label: 'Rodales', icon: 'plot', to: { name: 'admin-crud', params: { entity: 'rodales' } } },
        { key: 'acceso', label: 'Configuración de Acceso', icon: 'settings', to: { name: 'admin-configuracion' } },
      ],
    })
  }

  sections.push({
    key: 'combustible',
    label: 'Combustible',
    items: [
      { key: 'carga-combustible', label: 'Carga de Combustible', icon: 'fuel', to: { name: 'combustible' } },
    ],
  })

  const produccionItems = [
    { key: 'carga-produccion', label: 'Carga de Producción', icon: 'production', to: { name: 'produccion' } },
    { key: 'pendientes', label: 'Pendientes', icon: 'pending', to: { name: 'pendientes' }, badge: produccionStore.pendingCount },
  ]

  if (!isEncargado.value || isAdmin.value) {
    produccionItems.push({ key: 'mis-registros', label: 'Mis Registros', icon: 'records', to: { name: 'mis-registros' } })
  }

  sections.push({ key: 'produccion', label: 'Producción', items: produccionItems })
  return sections
})

function toggleSection(key) {
  openSections[key] = !openSections[key]
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function navItemClass(active) {
  return [
    'relative flex min-h-11 items-center gap-2 rounded-lg border py-2 text-sm font-semibold transition-all duration-150 ease-out hover:-translate-y-px active:translate-y-0 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30',
    sidebarCollapsed.value ? 'md:justify-center md:px-2 justify-between px-3' : 'justify-between px-3',
    active
      ? 'border-[#10B981]/45 bg-[#0F2A1E] text-white shadow-[inset_4px_0_0_#10B981,0_0_18px_rgba(16,185,129,0.08)]'
      : 'border-transparent bg-transparent text-white/82 hover:border-[#222D26] hover:bg-[#141C17] hover:text-white',
  ]
}

function navSectionClass(section) {
  const active = isSectionActive(section)
  const open = openSections[section.key]

  return [
    'flex w-full items-center rounded-lg border py-2 text-left text-sm font-semibold transition-all duration-150 ease-out hover:-translate-y-px active:translate-y-0 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30',
    sidebarCollapsed.value ? 'md:justify-center md:px-2 justify-between px-3' : 'justify-between px-3',
    active
      ? 'border-[#10B981]/30 bg-[#141C17] text-[#B1F0D6]'
      : open
        ? 'border-transparent bg-[#141C17]/75 text-white'
        : 'border-transparent bg-transparent text-white/78 hover:bg-[#141C17] hover:text-white',
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

watch(sidebarCollapsed, (value) => {
  localStorage.setItem('sidebarCollapsed', value ? '1' : '0')
})

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
