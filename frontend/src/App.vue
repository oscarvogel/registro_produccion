<template>
  <div id="app" class="app-shell min-h-screen">
    <OfflineBanner
      :pending-count="produccionStore.pendingCount"
      :has-cached-session="hasCachedSession"
    />

    <template v-if="authStore.isAuthenticated">
      <div :class="['min-h-screen', connectivityStore.isOffline ? 'pt-8' : '']">
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
              <p class="truncate text-xs font-semibold text-[#9FE1CB]">{{ userRoleLabel }} - {{ connectivityStore.isOnline ? 'En línea' : 'Sin conexión' }}</p>
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
                  {{ userRoleLabel }} - {{ connectivityStore.isOnline ? 'En línea' : 'Sin conexión' }}
                </p>
              </div>
            </div>
          </div>

          <nav :class="['min-h-0 flex-1 overflow-y-auto py-3', sidebarCollapsed ? 'md:px-2 px-2' : 'px-2']">
            <div :class="sidebarCollapsed ? 'space-y-1.5' : 'space-y-2'">
              <template v-for="area in navigationAreas" :key="area.key">
                <router-link
                  v-if="area.type === 'link'"
                  :to="area.to"
                  :class="navItemClass(isItemActive(area))"
                  :title="sidebarCollapsed ? area.label : undefined"
                  @click="mobileMenuOpen = false"
                >
                  <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
                    <AppIcon :name="area.icon" size="sm" class="shrink-0" />
                    <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">{{ area.label }}</span>
                  </span>
                </router-link>

                <section v-else>
                  <button
                    type="button"
                    :class="navSectionClass(area)"
                    :title="sidebarCollapsed ? area.label : undefined"
                    :aria-expanded="openSection === area.key"
                    :aria-controls="sectionPanelId(area.key)"
                    @click="toggleSection(area.key)"
                  >
                    <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
                      <AppIcon :name="area.icon" size="sm" class="shrink-0" />
                      <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">{{ area.label }}</span>
                    </span>
                    <AppIcon
                      name="chevronDown"
                      size="xs"
                      :class="['shrink-0 transition-transform', sidebarCollapsed ? 'md:hidden' : '', openSection === area.key ? 'rotate-180' : '']"
                    />
                  </button>

                  <Transition name="nav-section">
                    <div
                      v-show="openSection === area.key"
                      :id="sectionPanelId(area.key)"
                      :class="['mt-1 space-y-1 overflow-hidden', sidebarCollapsed ? 'md:hidden' : '']"
                    >
                      <router-link
                        v-for="item in area.items"
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
              </template>
            </div>
          </nav>

          <div :class="['shrink-0 border-t border-[#222D26] p-2', sidebarCollapsed ? 'md:px-2' : '']">
            <router-link
              :to="{ name: 'manuales' }"
              :class="navItemClass(route.name === 'manuales')"
              :title="sidebarCollapsed ? 'Manuales' : undefined"
              @click="mobileMenuOpen = false"
            >
              <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
                <AppIcon name="manual" size="sm" />
                <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">Manuales</span>
              </span>
            </router-link>

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
import { computed, onMounted, onUnmounted, provide, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import { useConnectivityStore } from '@/stores/connectivity'
import { useTheme } from '@/composables/useTheme'
import OfflineBanner from '@/components/ui/OfflineBanner.vue'
import ToastHost from '@/components/ToastHost.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { createNavigationAreas } from '@/config/navigation'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const produccionStore = useProduccionStore()
const connectivityStore = useConnectivityStore()
const { isDark, toggleTheme } = useTheme()
const mobileMenuOpen = ref(false)
const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === '1')
const openSection = ref(null)

const isAdmin = computed(() => authStore.isAdmin)
const isEncargado = computed(() => authStore.user?.encargado === 1)

// Whether the operator has ever signed in on this device (has an offline
// session cache, valid or not). Drives the OfflineBanner copy: when false the
// banner explains the "first time" requirement instead of the generic cache
// reassurance.
const hasCachedSession = computed(() => !!authStore.cachedSession)

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

const navigationAreas = computed(() => createNavigationAreas({
  isAdmin: isAdmin.value,
  isEncargado: isEncargado.value,
  pendingCount: produccionStore.pendingCount,
}))

function toggleSection(key) {
  if (sidebarCollapsed.value) sidebarCollapsed.value = false
  openSection.value = openSection.value === key ? null : key
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  openSection.value = sidebarCollapsed.value ? null : activeSectionKey()
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
  const open = openSection.value === section.key

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
  if (item.activeRoutes?.includes(route.name)) return true
  if (item.to.name === 'admin-crud') {
    return route.name === 'admin-crud' && route.params.entity === item.to.params.entity
  }
  return route.name === item.to.name
}

function activeSectionKey() {
  return navigationAreas.value.find((area) => area.type === 'section' && isSectionActive(area))?.key || null
}

function sectionPanelId(key) {
  return `sidebar-section-${key}`
}

watch(
  [() => route.fullPath, () => isAdmin.value, () => isEncargado.value],
  () => {
    mobileMenuOpen.value = false
    if (!sidebarCollapsed.value) openSection.value = activeSectionKey()
  },
  { immediate: true },
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

// Offline / sync management.
// `isOnline` now lives in the connectivity store — it is updated by window
// events registered in main.js via `connectivityStore.init()`.
const SYNC_INTERVAL_MS = 5 * 60 * 1000
let syncIntervalId = null

async function handleOnline() {
  // The connectivity store handles the boolean; here we just kick off the
  // sync when we come back online while authenticated.
  if (authStore.isAuthenticated) {
    await produccionStore.syncPending()
  }
}

onMounted(() => {
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.addEventListener('appinstalled', handleAppInstalled)
  window.addEventListener('online', handleOnline)
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
  if (syncIntervalId) clearInterval(syncIntervalId)
})

function handleLogout() {
  authStore.logout()
  mobileMenuOpen.value = false
  router.push({ name: 'login' })
}
</script>
