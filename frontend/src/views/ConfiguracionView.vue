<template>
  <div class="flex min-h-[calc(100vh-8.5rem)] flex-col items-center bg-neutral-100 px-3 pb-5 pt-4 md:min-h-[calc(100vh-3.5rem)] md:px-4">
    <div class="flex w-full max-w-2xl flex-col items-center">

      <h1 class="mb-4 text-center text-2xl font-extrabold uppercase leading-tight text-neutral-950 md:text-3xl">
        Configuración
      </h1>

      <!-- Apariencia -->
      <div class="app-card mb-3 w-full rounded-xl p-4">
        <div class="mb-3 flex items-center gap-3">
          <div class="w-11 h-11 rounded-xl bg-info-light flex items-center justify-center flex-shrink-0">
            <AppIcon :name="isDark ? 'moon' : 'sun'" size="lg" class="text-info-dark" />
          </div>
          <div>
            <h2 class="text-lg font-bold text-neutral-800">Apariencia</h2>
            <p class="text-sm text-neutral-500">Tu preferencia queda guardada en este dispositivo.</p>
          </div>
        </div>

        <button
          type="button"
          class="flex w-full items-center justify-between rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-3.5 text-left transition-all duration-150 ease-out hover:-translate-y-px hover:border-secondary/30 hover:bg-white active:translate-y-0 active:scale-[0.99]"
          @click="toggleTheme"
        >
          <span>
            <span class="block text-sm font-extrabold text-neutral-800">{{ isDark ? 'Modo oscuro activo' : 'Modo claro activo' }}</span>
            <span class="block text-xs font-semibold text-neutral-500">{{ isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro' }}</span>
          </span>
          <span
            :class="[
              'h-7 w-12 rounded-full border p-0.5 transition-colors',
              isDark ? 'border-primary/30 bg-primary-dark' : 'border-secondary/20 bg-secondary-light',
            ]"
          >
            <span
              :class="[
                'flex h-6 w-6 items-center justify-center rounded-full bg-white text-info-dark shadow-sm transition-transform duration-200',
                isDark ? 'translate-x-0' : 'translate-x-5',
              ]"
            >
              <AppIcon :name="isDark ? 'moon' : 'sun'" size="xs" />
            </span>
          </span>
        </button>
      </div>

      <!-- Instalar app -->
      <div class="app-card mb-3 w-full rounded-xl p-4">
        <div class="mb-3 flex items-center gap-3">
          <div class="w-11 h-11 rounded-xl bg-info-light flex items-center justify-center flex-shrink-0">
            <AppIcon name="download" size="lg" class="text-info-dark" />
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
            <AppIcon name="download" :stroke-width="2.5" />
            Instalar App
          </button>
        </template>

        <template v-else>
          <div class="w-full bg-neutral-50 border border-neutral-200 rounded-xl px-5 py-3.5 flex items-center gap-3">
            <AppIcon name="success" :stroke-width="2.5" class="text-success flex-shrink-0" />
            <span class="text-sm text-neutral-600">
              La aplicación ya está instalada o la instalación no está disponible en este navegador.
            </span>
          </div>
        </template>
      </div>

      <!-- Cerrar sesión -->
      <button
        @click="handleLogout"
        class="app-card flex w-full items-center gap-3 rounded-xl px-4 py-3.5 transition-transform duration-150 active:scale-[0.98] hover:border-error/40"
      >
        <div class="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-error-light">
          <AppIcon name="logout" size="lg" :stroke-width="2.1" class="text-error" />
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
import { useTheme } from '@/composables/useTheme'
import AppIcon from '@/components/ui/AppIcon.vue'

const router = useRouter()
const authStore = useAuthStore()
const pwaInstall = inject('pwaInstall')
const { isDark, toggleTheme } = useTheme()

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>
