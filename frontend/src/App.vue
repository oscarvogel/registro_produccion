<template>
  <div id="app" class="min-h-screen bg-neutral-100">
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
        <div class="grid grid-cols-2 h-20 px-5 pb-1.5">
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
        </div>
      </nav>
    </template>

    <router-view v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isProduccionRoute = computed(() => route.name === 'produccion')

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>
