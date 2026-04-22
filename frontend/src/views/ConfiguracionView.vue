<template>
  <div class="min-h-[calc(100vh-8.5rem)] md:min-h-[calc(100vh-3.5rem)] flex flex-col items-center pt-8 pb-6 px-5 bg-neutral-100">
    <div class="w-full max-w-md flex flex-col items-center">

      <h1 class="text-2xl md:text-3xl font-extrabold text-primary-dark uppercase text-center leading-tight mb-7">
        Configuración
      </h1>

      <!-- Instalar app -->
      <div class="w-full bg-white rounded-[1.4rem] shadow-sm border border-neutral-200 p-6 mb-4">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-11 h-11 rounded-xl bg-primary-light/25 flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-primary-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold text-neutral-800">Instalar aplicación</h2>
            <p class="text-sm text-neutral-500">Accedé más rápido desde tu pantalla de inicio</p>
          </div>
        </div>

        <template v-if="pwaInstall.deferredInstallPrompt.value">
          <button
            @click="pwaInstall.installApp()"
            class="w-full bg-primary-dark text-white rounded-xl px-5 py-3.5 flex items-center justify-center gap-2.5 font-semibold text-base shadow-[0_4px_16px_rgba(20,61,35,0.30)] active:scale-[0.98] transition-transform duration-150"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Instalar App
          </button>
        </template>

        <template v-else>
          <div class="w-full bg-neutral-50 border border-neutral-200 rounded-xl px-5 py-3.5 flex items-center gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-success flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <span class="text-sm text-neutral-600">
              La aplicación ya está instalada o la instalación no está disponible en este navegador.
            </span>
          </div>
        </template>
      </div>

      <!-- Cerrar sesión -->
      <button
        @click="handleLogout"
        class="w-full bg-white rounded-[1.4rem] py-5 px-6 flex items-center gap-4 shadow-sm border border-neutral-200 active:scale-[0.98] transition-transform duration-150 hover:border-error/40"
      >
        <div class="w-12 h-12 rounded-[0.9rem] bg-red-50 flex items-center justify-center flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 text-error">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </div>
        <span class="text-[1.1rem] font-extrabold text-error tracking-wide uppercase">Cerrar sesión</span>
      </button>

    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const pwaInstall = inject('pwaInstall')

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>
