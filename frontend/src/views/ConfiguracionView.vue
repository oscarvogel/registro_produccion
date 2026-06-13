<template>
  <div class="min-h-[calc(100vh-8.5rem)] bg-[var(--app-bg)] px-3 py-3 pb-20 md:min-h-[calc(100vh-3.5rem)] md:px-4 md:py-4">
    <div class="mx-auto flex w-full max-w-3xl flex-col gap-3">
      <PageHeader title="Configuración" description="Preferencias locales, instalación y sesión." />

      <section class="app-card w-full rounded-xl p-3.5">
        <div class="mb-3 flex items-center gap-3">
          <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-info-light">
            <AppIcon :name="isDark ? 'moon' : 'sun'" size="lg" class="text-info-dark" />
          </div>
          <div class="min-w-0">
            <h2 class="text-base font-extrabold text-neutral-800">Apariencia</h2>
            <p class="text-sm text-neutral-500">Tu preferencia queda guardada en este dispositivo.</p>
          </div>
        </div>

        <button
          type="button"
          class="app-surface-muted flex min-h-12 w-full items-center justify-between gap-3 rounded-lg border px-3.5 py-2.5 text-left transition-all duration-150 ease-out hover:-translate-y-px hover:border-secondary/30 active:translate-y-0 active:scale-[0.99]"
          @click="toggleTheme"
        >
          <span class="min-w-0">
            <span class="block text-sm font-extrabold text-neutral-800">{{ isDark ? 'Modo oscuro activo' : 'Modo claro activo' }}</span>
            <span class="block text-xs font-semibold text-neutral-500">{{ isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro' }}</span>
          </span>
          <span
            :class="[
              'h-7 w-12 shrink-0 rounded-full border p-0.5 transition-colors',
              isDark ? 'border-primary/30 bg-primary-dark' : 'border-secondary/20 bg-secondary-light',
            ]"
          >
            <span
              :class="[
                'app-card flex h-6 w-6 items-center justify-center rounded-full text-info-dark shadow-sm transition-transform duration-200',
                isDark ? 'translate-x-0' : 'translate-x-5',
              ]"
            >
              <AppIcon :name="isDark ? 'moon' : 'sun'" size="xs" />
            </span>
          </span>
        </button>
      </section>

      <section class="app-card w-full rounded-xl p-3.5">
        <div class="mb-3 flex items-center gap-3">
          <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-info-light">
            <AppIcon name="download" size="lg" class="text-info-dark" />
          </div>
          <div class="min-w-0">
            <h2 class="text-base font-extrabold text-neutral-800">Instalar aplicación</h2>
            <p class="text-sm text-neutral-500">Accedé más rápido desde tu pantalla de inicio.</p>
          </div>
        </div>

        <template v-if="pwaInstall?.deferredInstallPrompt?.value">
          <AppButton block @click="pwaInstall.installApp()">
            <AppIcon name="download" :stroke-width="2.5" />
            Instalar App
          </AppButton>
        </template>

        <template v-else>
          <div class="app-surface-muted flex w-full items-center gap-3 rounded-lg border px-3.5 py-2.5">
            <AppIcon name="success" :stroke-width="2.5" class="flex-shrink-0 text-success" />
            <span class="text-sm text-neutral-600">
              La aplicación ya está instalada o la instalación no está disponible en este navegador.
            </span>
          </div>
        </template>
      </section>

      <button
        type="button"
        class="app-card flex min-h-14 w-full items-center gap-3 rounded-xl px-3.5 py-3 text-left transition-transform duration-150 active:scale-[0.98] hover:border-error/40"
        @click="handleLogout"
      >
        <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-error-light">
          <AppIcon name="logout" size="lg" :stroke-width="2.1" class="text-error" />
        </div>
        <span class="text-base font-extrabold uppercase tracking-wide text-error">Cerrar sesión</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import PageHeader from '@/components/ui/PageHeader.vue'

const router = useRouter()
const authStore = useAuthStore()
const pwaInstall = inject('pwaInstall')
const { isDark, toggleTheme } = useTheme()

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>
