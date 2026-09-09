<template>
  <div
    id="app"
    :class="['app-shell min-h-screen', connectivityStore.isOfflineOrBackendDown ? 'app-has-offline-banner' : '']"
  >
    <OfflineBanner
      :pending-count="produccionStore.pendingCount"
      :has-cached-session="hasCachedSession"
    />

    <template v-if="authStore.isAuthenticated">
      <div :class="['min-h-screen', connectivityStore.isOfflineOrBackendDown ? 'pt-[var(--app-offline-banner-height)]' : '']">
        <header class="app-mobile-header sticky z-30 border-b border-[var(--app-nav-border)] bg-[var(--app-nav-header)] text-[var(--app-nav-text)] md:hidden">
          <div class="flex h-[var(--app-mobile-header-height)] items-center justify-between px-4">
            <button
              ref="mobileMenuButton"
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-lg border border-[var(--app-nav-control-border)] text-[var(--app-nav-text)]"
              aria-label="Abrir navegacion"
              aria-controls="app-mobile-navigation"
              :aria-expanded="mobileMenuOpen"
              @click="openMobileMenu"
            >
              <AppIcon name="menu" />
            </button>
            <div class="min-w-0 px-3 text-center">
              <p class="truncate text-sm font-extrabold text-[var(--app-nav-text)]">Registro Producción</p>
              <p class="truncate text-xs font-semibold text-[var(--app-nav-status-text)]">{{ userRoleLabel }} - {{ backendConnectionLabel }}</p>
            </div>
            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-lg border border-[var(--app-nav-control-border)] text-[var(--app-nav-text-soft)]"
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
            @click="closeMobileMenu"
          ></div>
        </Transition>

        <aside
          ref="mobileNavigation"
          id="app-mobile-navigation"
          aria-label="Navegacion principal"
          :class="[
            'app-navigation fixed left-0 z-50 flex w-72 max-w-[86vw] flex-col border-r border-[var(--app-nav-border)] bg-[var(--app-nav-bg)] text-[var(--app-nav-text)] shadow-xl transition-[transform,width] duration-200 md:z-20 md:max-w-none md:translate-x-0 md:shadow-none',
            sidebarCollapsed ? 'md:w-20' : 'md:w-64',
            mobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
          ]"
        >
          <div :class="['flex h-[58px] shrink-0 items-center border-b border-[var(--app-nav-border)] bg-[var(--app-nav-header)] px-3', sidebarCollapsed ? 'md:justify-center md:px-3' : 'justify-between']">
            <div :class="['flex min-w-0 items-center gap-3', sidebarCollapsed ? 'md:hidden' : '']">
              <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[var(--app-nav-accent)] p-1 shadow-[0_0_18px_var(--app-nav-logo-glow)] ring-1 ring-[var(--app-nav-logo-ring)]">
                <img src="/logo-forestal.png" alt="" class="h-full w-full object-contain" />
              </span>
              <span class="min-w-0">
                <p class="truncate text-sm font-extrabold leading-tight text-[var(--app-nav-text)]">Registro</p>
                <p class="truncate text-xs font-bold leading-tight text-[var(--app-nav-accent-strong)]">Producción</p>
              </span>
            </div>
            <button
              type="button"
              class="hidden h-9 w-9 items-center justify-center rounded-lg text-[var(--app-nav-control-text)] hover:bg-[var(--app-nav-control-border)] hover:text-[var(--app-nav-text)] md:flex"
              :aria-label="sidebarCollapsed ? 'Expandir navegacion' : 'Contraer navegacion'"
              @click="toggleSidebar"
            >
              <AppIcon name="menu" size="sm" />
            </button>
            <button
              type="button"
              class="flex h-9 w-9 items-center justify-center rounded-lg text-[var(--app-nav-control-text)] hover:bg-[var(--app-nav-control-border)] md:hidden"
              aria-label="Cerrar menu"
              @click="closeMobileMenu"
            >
              <AppIcon name="close" size="sm" />
            </button>
          </div>

          <div :class="['border-b border-[var(--app-nav-border)] px-3 py-3', sidebarCollapsed ? 'md:hidden' : '']">
            <div class="flex items-center gap-3">
              <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[var(--app-nav-user-bg)] text-sm font-extrabold text-[var(--app-nav-user-text)] ring-1 ring-[var(--app-nav-user-ring)]">
                {{ userInitials }}
              </span>
              <div class="min-w-0">
                <p class="truncate text-sm font-extrabold uppercase text-[var(--app-nav-text)]">{{ authStore.userName }}</p>
                <p class="flex items-center gap-1.5 text-xs font-medium text-[var(--app-nav-text)]">
                  <span class="app-led h-1.5 w-1.5 rounded-full bg-[var(--app-nav-status)] text-[var(--app-nav-status)]"></span>
                  {{ userRoleLabel }} - {{ backendConnectionLabel }}
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
                exact-active-class="!border-[var(--app-nav-active-border)] !bg-[var(--app-nav-active-bg)] !text-[var(--app-nav-text)]"
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
                  :aria-label="sidebarCollapsed ? section.label : undefined"
                  @click="toggleSection(section.key)"
                >
                  <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-2' : 'gap-2']">
                    <span
                      :class="[
                        'rounded-full transition-colors',
                        sidebarCollapsed ? 'md:h-2 md:w-2 h-1.5 w-1.5' : 'h-1.5 w-1.5',
                        isSectionActive(section) ? 'bg-[var(--app-nav-status)]' : 'bg-[var(--app-nav-muted-indicator)]',
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
                          'rounded-full bg-warning text-[10px] font-extrabold text-on-warning',
                          sidebarCollapsed ? 'md:absolute md:right-2 md:top-2 md:h-2 md:w-2 md:px-0 md:py-0 md:text-transparent ml-2 px-2 py-0.5' : 'ml-2 px-2 py-0.5',
                        ]"
                      >
                        {{ item.badge }}
                      </span>
                    </router-link>
                  </div>
                </Transition>
              </section>

              <router-link
                v-for="item in trailingItems"
                :key="item.key"
                :to="item.to"
                :class="navItemClass(isItemActive(item))"
                :title="sidebarCollapsed ? item.label : undefined"
                exact-active-class="!border-[var(--app-nav-active-border)] !bg-[var(--app-nav-active-bg)] !text-[var(--app-nav-text)]"
                @click="mobileMenuOpen = false"
              >
                <span :class="['flex min-w-0 items-center', sidebarCollapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
                  <AppIcon :name="item.icon" size="sm" class="shrink-0" />
                  <span :class="['truncate', sidebarCollapsed ? 'md:hidden' : '']">{{ item.label }}</span>
                </span>
              </router-link>
            </div>
          </nav>

          <div :class="['shrink-0 border-t border-[var(--app-nav-border)] p-2', sidebarCollapsed ? 'md:px-2' : '']">
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
                  'ml-2 h-5 w-9 rounded-full border border-[var(--app-nav-control-border)] p-0.5 transition-colors',
                  isDark ? 'bg-[var(--app-nav-toggle-off-bg)]' : 'bg-secondary-light/80',
                  sidebarCollapsed ? 'md:hidden' : '',
                ]"
              >
                <span
                  :class="[
                    'block h-4 w-4 rounded-full bg-[var(--app-nav-text)] shadow-sm transition-transform duration-200',
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
              :aria-label="sidebarCollapsed ? 'Salir' : undefined"
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
import { computed, nextTick, onMounted, onUnmounted, provide, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import { useConnectivityStore } from '@/stores/connectivity'
import { useTheme } from '@/composables/useTheme'
import OfflineBanner from '@/components/ui/OfflineBanner.vue'
import ToastHost from '@/components/ToastHost.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { createSidebarNavigation } from '@/config/navigation'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const produccionStore = useProduccionStore()
const connectivityStore = useConnectivityStore()
const { isDark, toggleTheme } = useTheme()
const mobileMenuOpen = ref(false)
const mobileMenuButton = ref(null)
const mobileNavigation = ref(null)
const previouslyFocusedElement = ref(null)
let previousBodyOverflow = ''
const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === '1')
const openSections = reactive({
  operacion: false,
  combustible: false,
  produccion: false,
})

const isAdmin = computed(() => authStore.isAdmin)
const isEncargado = computed(() => authStore.user?.encargado === 1)
const backendConnectionLabel = computed(() => {
  if (!connectivityStore.isOnline) return 'Sin conexión'
  if (connectivityStore.pendingInitialHealthCheck) return 'Verificando servidor'
  return connectivityStore.isBackendUp ? 'Servidor disponible' : 'Servidor no disponible'
})

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

const sidebarNavigation = computed(() => createSidebarNavigation({
  isAdmin: isAdmin.value,
  isEncargado: isEncargado.value,
  pendingCount: produccionStore.pendingCount,
}))
const primaryItems = computed(() => sidebarNavigation.value.primaryItems)
const navSections = computed(() => sidebarNavigation.value.sections)
const trailingItems = computed(() => sidebarNavigation.value.trailingItems)

function toggleSection(key) {
  openSections[key] = !openSections[key]
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function getMobileFocusableElements() {
  const candidates = Array.from(mobileNavigation.value?.querySelectorAll(
    'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
  ) || [])

  return candidates.filter((element) => {
    let current = element
    while (current && current !== mobileNavigation.value) {
      if (current.hidden || window.getComputedStyle(current).display === 'none') return false
      current = current.parentElement
    }
    return true
  })
}

async function focusMobileMenu() {
  await nextTick()
  getMobileFocusableElements()[0]?.focus()
}

function openMobileMenu() {
  if (mobileMenuOpen.value) return
  previouslyFocusedElement.value = document.activeElement
  mobileMenuOpen.value = true
}

function closeMobileMenu({ restoreFocus = true } = {}) {
  if (!mobileMenuOpen.value) return
  if (!restoreFocus) previouslyFocusedElement.value = null
  mobileMenuOpen.value = false
}

function handleMobileMenuKeydown(event) {
  if (!mobileMenuOpen.value) return

  if (event.key === 'Escape') {
    event.preventDefault()
    closeMobileMenu()
    return
  }

  if (event.key !== 'Tab') return
  const focusable = getMobileFocusableElements()
  if (focusable.length === 0) return

  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

function navItemClass(active) {
  return [
    'relative flex min-h-11 items-center gap-2 rounded-lg border py-2 text-sm font-semibold transition-all duration-150 ease-out hover:-translate-y-px active:translate-y-0 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30',
    sidebarCollapsed.value ? 'md:justify-center md:px-2 justify-between px-3' : 'justify-between px-3',
    active
      ? 'border-[var(--app-nav-active-border)] bg-[var(--app-nav-active-bg)] text-[var(--app-nav-text)] shadow-[inset_4px_0_0_var(--app-nav-accent),0_0_18px_var(--app-nav-active-glow)]'
      : 'border-transparent bg-transparent text-[var(--app-nav-text-muted)] hover:border-[var(--app-nav-border)] hover:bg-[var(--app-nav-surface)] hover:text-[var(--app-nav-text)]',
  ]
}

function navSectionClass(section) {
  const active = isSectionActive(section)
  const open = openSections[section.key]

  return [
    'flex w-full items-center rounded-lg border py-2 text-left text-sm font-semibold transition-all duration-150 ease-out hover:-translate-y-px active:translate-y-0 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30',
    sidebarCollapsed.value ? 'md:justify-center md:px-2 justify-between px-3' : 'justify-between px-3',
    active
      ? 'border-[var(--app-nav-active-border-soft)] bg-[var(--app-nav-surface)] text-[var(--app-nav-user-text)]'
      : open
        ? 'border-transparent bg-[var(--app-nav-surface-open)] text-[var(--app-nav-text)]'
        : 'border-transparent bg-transparent text-[var(--app-nav-text-subtle)] hover:bg-[var(--app-nav-surface)] hover:text-[var(--app-nav-text)]',
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

watch(
  () => route.fullPath,
  () => {
    closeMobileMenu()
  },
)

watch(mobileMenuOpen, async (open, wasOpen) => {
  if (open) {
    if (!previouslyFocusedElement.value) previouslyFocusedElement.value = document.activeElement
    previousBodyOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    await focusMobileMenu()
    return
  }

  document.body.style.overflow = previousBodyOverflow
  previousBodyOverflow = ''
  if (wasOpen) {
    await nextTick()
    const target = previouslyFocusedElement.value?.isConnected
      ? previouslyFocusedElement.value
      : mobileMenuButton.value
    target?.focus?.()
  }
  previouslyFocusedElement.value = null
})

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
const SYNC_INTERVAL_MS = 30 * 1000
let syncIntervalId = null

async function attemptPendingSync({ forceHealthCheck = false } = {}) {
  if (!authStore.isAuthenticated || !navigator.onLine) return
  const backendUp = await connectivityStore.refreshBackendHealth({ force: forceHealthCheck })
  if (backendUp) {
    await produccionStore.syncPending()
  }
}

async function handleOnline() {
  await attemptPendingSync({ forceHealthCheck: true })
}

onMounted(() => {
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.addEventListener('appinstalled', handleAppInstalled)
  window.addEventListener('online', handleOnline)
  document.addEventListener('keydown', handleMobileMenuKeydown)
  if (authStore.isAuthenticated) {
    produccionStore.refreshPendingCount().then(() => attemptPendingSync({ forceHealthCheck: true }))
  }

  syncIntervalId = setInterval(async () => {
    await attemptPendingSync()
  }, SYNC_INTERVAL_MS)
})

onUnmounted(() => {
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.removeEventListener('appinstalled', handleAppInstalled)
  window.removeEventListener('online', handleOnline)
  document.removeEventListener('keydown', handleMobileMenuKeydown)
  document.body.style.overflow = previousBodyOverflow
  if (syncIntervalId) clearInterval(syncIntervalId)
})

function handleLogout() {
  authStore.logout()
  closeMobileMenu({ restoreFocus: false })
  router.push({ name: 'login' })
}
</script>
