<template>
  <div id="app" class="min-h-screen bg-neutral-100">
    <!-- Offline banner -->
    <div
      v-if="!isOnline"
      class="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 bg-amber-500 text-white text-xs font-semibold py-1.5 px-3"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M1 1l22 22" /><path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55" /><path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39" /><path d="M10.71 5.05A16 16 0 0 1 22.56 9" /><path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88" /><path d="M8.53 16.11a6 6 0 0 1 6.95 0" /><line x1="12" x2="12.01" y1="20" y2="20" />
      </svg>
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
                  class="px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  Inicio
                </router-link>
                <router-link
                  to="/produccion"
                  class="px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  Producción
                </router-link>
                <router-link
                  to="/dashboard"
                  class="px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                  active-class="!bg-primary-light/20 !text-primary-dark"
                  exact-active-class="!bg-primary-light/20 !text-primary-dark"
                >
                  Dashboard
                </router-link>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <span class="text-sm text-neutral-500">{{ authStore.userName }}</span>
              <button
                @click="handleLogout"
                class="px-3 py-1.5 text-sm font-medium text-neutral-600 hover:text-error border border-neutral-300 hover:border-error rounded-lg transition-colors"
              >
                Salir
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main :class="isProduccionRoute ? 'pb-0 md:pb-0' : 'pb-[5.5rem] md:pb-0'">
        <router-view />
      </main>

      <nav v-if="!isProduccionRoute" class="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-neutral-200">
        <div class="h-20 px-5 pb-1.5 grid grid-cols-3">
          <router-link
            to="/"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-16 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 10.5 12 3l9 7.5" />
                <path d="M5 9.8V21h14V9.8" />
                <path d="M9 21v-6h6v6" />
              </svg>
            </span>
            <span class="text-sm font-semibold">Inicio</span>
          </router-link>
          <router-link
            to="/produccion"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-16 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7z" />
                <path d="M8 5v4h8V5" />
                <path d="M8 13h8" />
              </svg>
            </span>
            <span class="text-sm font-semibold">Producción</span>
          </router-link>
          <router-link
            to="/dashboard"
            class="group relative flex flex-col items-center justify-center gap-1.5 rounded-xl text-neutral-500"
            exact-active-class="!text-primary"
          >
            <span class="absolute -top-px h-1.5 w-16 rounded-b-xl bg-transparent group-[.router-link-exact-active]:bg-primary"></span>
            <span class="flex h-12 w-12 items-center justify-center rounded-3xl bg-transparent group-[.router-link-exact-active]:bg-primary-light/30">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" class="h-6 w-6">
                <rect x="3" y="3" width="7" height="7" rx="1"/>
                <rect x="14" y="3" width="7" height="7" rx="1"/>
                <rect x="3" y="14" width="7" height="7" rx="1"/>
                <rect x="14" y="14" width="7" height="7" rx="1"/>
              </svg>
            </span>
            <span class="text-sm font-semibold">Dashboard</span>
          </router-link>
        </div>
      </nav>
    </template>

    <router-view v-else />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const produccionStore = useProduccionStore()
const isProduccionRoute = computed(() => route.name === 'produccion')

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
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)

  // Periodic sync every 5 minutes when online
  syncIntervalId = setInterval(async () => {
    if (navigator.onLine && authStore.isAuthenticated) {
      await produccionStore.syncPending()
    }
  }, SYNC_INTERVAL_MS)
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
  if (syncIntervalId) clearInterval(syncIntervalId)
})

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>
