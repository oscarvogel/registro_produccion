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

        <template v-if="isPwaStandalone">
          <div
            data-testid="pwa-installed-message"
            class="app-surface-muted flex w-full items-center gap-3 rounded-lg border px-3.5 py-2.5"
          >
            <AppIcon name="success" :stroke-width="2.5" class="flex-shrink-0 text-success" />
            <span class="text-sm font-semibold text-neutral-600">
              Ya tenés la app instalada en tu pantalla de inicio.
            </span>
          </div>
        </template>

        <template v-else>
          <AppButton
            v-if="canInstallPwa"
            data-testid="pwa-install-button"
            block
            @click="pwaInstall?.installApp()"
          >
            <AppIcon name="download" :stroke-width="2.5" />
            Instalar App
          </AppButton>

          <div
            v-else
            data-testid="pwa-manual-install"
            class="app-surface-muted w-full rounded-lg border px-3.5 py-3"
          >
            <div class="flex items-start gap-3">
              <AppIcon
                name="warning"
                :stroke-width="2.5"
                class="mt-0.5 flex-shrink-0 text-warning-dark"
              />
              <div class="min-w-0 text-sm text-neutral-600">
                <p class="font-bold text-neutral-800">
                  {{ isXiaomiBrowser
                    ? 'Mi Browser no ofrece el botón automático de instalación.'
                    : 'Este navegador no ofrece el botón automático de instalación.'
                  }}
                </p>
                <p class="mt-1">Podés agregar la app manualmente:</p>
                <ol class="mt-2 list-decimal space-y-1 pl-5">
                  <li>Tocá el menú <span aria-label="tres puntos verticales">⋮</span> del navegador.</li>
                  <li>Elegí <strong>Agregar a la pantalla de inicio</strong>.</li>
                  <li>Confirmá el acceso directo.</li>
                </ol>
              </div>
            </div>
          </div>

          <a
            data-testid="chrome-play-link"
            :href="CHROME_PLAY_STORE_URL"
            target="_blank"
            rel="noopener noreferrer"
            class="app-button-soft mt-3 flex min-h-11 w-full items-center justify-center gap-2 rounded-lg border px-3.5 py-2.5 text-center text-sm font-bold transition hover:-translate-y-px hover:border-primary/35 focus:outline-none focus:ring-2 focus:ring-primary/20 active:translate-y-0"
          >
            <AppIcon name="download" size="sm" />
            <span>
              Si no podés instalar la app desde este navegador, instalá Chrome desde Google Play
            </span>
          </a>
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
import {
  CHROME_PLAY_STORE_URL,
  usePwaInstallStatus,
} from '@/composables/usePwaInstallStatus'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import PageHeader from '@/components/ui/PageHeader.vue'

const router = useRouter()
const authStore = useAuthStore()
const pwaInstall = inject('pwaInstall', null)
const { isDark, toggleTheme } = useTheme()
const {
  canInstall: canInstallPwa,
  isStandalone: isPwaStandalone,
  isXiaomiBrowser,
} = usePwaInstallStatus(pwaInstall)

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>
