<template>
  <div id="app" class="min-h-screen bg-neutral-100">
    <!-- Offline banner -->
    <div
      v-if="!isOnline"
      class="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 bg-amber-500 text-white text-xs font-semibold py-1.5 px-3"
    >
      <AppIcon name="offline" size="sm" :stroke-width="2.5" class="shrink-0" />
      Sin conexión · Los registros se guardarán localmente y se sincronizarán al reconectar
      <span v-if="produccionStore.pendingCount > 0" class="ml-1 bg-white/20 rounded px-1.5">{{ produccionStore.pendingCount }} pendiente{{ produccionStore.pendingCount !== 1 ? 's' : '' }}</span>
    </div>
    <template v-if="authStore.isAuthenticated">
      <header v-if="!isProduccionRoute" class="md:hidden bg-white border-b border-neutral-200">
        <div class="h-14 px-4 flex items-center justify-between">
          <span class="text-primary font-extrabold text-xl leading-none">Registro Producción</span>
          <div class="flex items-center gap-3">
            <button
              @click="handleLogout"
              class="px-4 py-1.5 text-xs font-semibold text-neutral-600 border border-neutral-300 rounded-full"
            >
              Salir
            </button>
          </div>
        </div>
      </header>

      <nav class="hidden md:block bg-white border-b border-neutral-200 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-14">
            <div class="flex items-center gap-6">
              <span class="text-primary-dark font-bold text-lg">Registro Producción</span>
              <div class="flex gap-1">
                <router-link
                  to="/"
                  class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  <AppIcon name="home" size="sm" />
                  Inicio
                </router-link>
                <router-link
                  to="/produccion"
                  class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  Producción
                </router-link>
                <router-link
                  to="/pendientes"
                  class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  <AppIcon name="pending" size="sm" />
                  Pendientes
                  <span v-if="produccionStore.pendingCount > 0" class="ml-1 rounded bg-warning/20 px-1.5 text-warning-dark">{{ produccionStore.pendingCount }}</span>
                </router-link>
                <router-link
                  v-if="authStore.user?.encargado !== 1"
                  to="/mis-registros"
                  class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  <AppIcon name="records" size="sm" />
                  Mis Registros
                </router-link>
                <router-link
                  v-if="authStore.user?.encargado === 1"
                  to="/dashboard"
                  class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  <AppIcon name="dashboard" size="sm" />
                  Dashboard
                </router-link>
                <router-link
                  v-if="authStore.isAdmin"
                  to="/admin"
                  class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  <AppIcon name="admin" size="sm" />
                  Admin
                </router-link>
                <router-link
                  to="/configuracion"
                  class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  Configuración
                </router-link>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <div class="text-right leading-tight">
                <p class="text-sm font-semibold text-neutral-700">{{ authStore.userName }}</p>
                <p class="text-xs text-neutral-400">{{ userRoleLabel }} · {{ isOnline ? 'En linea' : 'Sin conexion' }}</p>
              </div>
              <button
                @click="handleLogout"
                class="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-neutral-600 hover:text-error border border-neutral-300 hover:border-error rounded-lg transition-colors"
              >
                <AppIcon name="logout" size="sm" />
                Salir
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main :class="isProduccionRoute ? 'pb-0 md:pb-0' : 'pb-22 md:pb-0'">
        <router-view />
      </main>

      <nav v-if="!isProduccionRoute" class="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-neutral-200">
        <div :class="['h-20 px-1 pb-1.5 grid', authStore.isAdmin ? 'grid-cols-6' : 'grid-cols-5']">
          <router-link
            to="/"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-16 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <AppIcon name="home" size="lg" :stroke-width="2.2" />
            </span>
            <span class="text-xs font-semibold">Inicio</span>
          </router-link>
          <router-link
            to="/produccion"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-16 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <AppIcon name="production" size="lg" :stroke-width="2.1" />
            </span>
            <span class="text-xs font-semibold">Producción</span>
          </router-link>
          <router-link
            to="/pendientes"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-14 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="relative flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <AppIcon name="pending" size="lg" :stroke-width="2.1" />
              <span v-if="produccionStore.pendingCount > 0" class="absolute -right-1 -top-1 min-w-5 rounded-full bg-warning px-1 text-[10px] font-extrabold text-white">{{ produccionStore.pendingCount }}</span>
            </span>
            <span class="text-xs font-semibold">Cola</span>
          </router-link>
          <router-link
            v-if="authStore.user?.encargado !== 1"
            to="/mis-registros"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-16 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <AppIcon name="records" size="lg" :stroke-width="2.1" />
            </span>
            <span class="text-xs font-semibold">Registros</span>
          </router-link>
          <router-link
            v-if="authStore.user?.encargado === 1"
            to="/dashboard"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-16 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <AppIcon name="dashboard" size="lg" :stroke-width="2.1" />
            </span>
            <span class="text-xs font-semibold">Dashboard</span>
          </router-link>
          <router-link
            v-if="authStore.isAdmin"
            to="/admin"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-16 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <AppIcon name="admin" size="lg" :stroke-width="2.1" />
            </span>
            <span class="text-xs font-semibold">Admin</span>
          </router-link>
          <router-link
            to="/configuracion"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-16 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <AppIcon name="settings" size="lg" :stroke-width="2.1" />
            </span>
            <span class="text-xs font-semibold">Config</span>
          </router-link>
        </div>
      </nav>
    </template>

    <router-view v-else />
    <ToastHost />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, provide, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import ToastHost from '@/components/ToastHost.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const produccionStore = useProduccionStore()
const isProduccionRoute = computed(() => route.name === 'produccion')
const userRoleLabel = computed(() => {
  if (authStore.isAdmin) return 'Admin'
  if (authStore.user?.encargado === 1) return 'Encargado'
  return 'Operador'
})

// ─── PWA install prompt ───
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
    console.error('No se pudo mostrar el prompt de instalación:', error)
  }
}

provide('pwaInstall', { deferredInstallPrompt, installApp })

// ─── Offline / sync management ───
const isOnline = ref(navigator.onLine)
const SYNC_INTERVAL_MS = 5 * 60 * 1000 // 5 minutes
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

  // Periodic sync every 5 minutes when online
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
  router.push({ name: 'login' })
}
</script>
