<template>
  <div class="login-shell min-h-screen bg-neutral-950 px-4 py-6 text-neutral-900">
    <!-- Desktop -->
    <div class="hidden min-h-[calc(100vh-3rem)] items-center justify-center lg:flex">
      <section class="grid min-h-[34rem] w-full max-w-6xl grid-cols-[1.05fr_1fr] overflow-hidden rounded-[1.5rem] border-[10px] border-white bg-transparent shadow-2xl">
        <aside class="relative min-h-[34rem] overflow-hidden rounded-[1rem] p-10 text-white">
          <div class="absolute inset-0 bg-[linear-gradient(rgba(0,24,20,0.12),rgba(0,12,10,0.76))]"></div>
          <img src="/logo-forestal.png" alt="Logo Forestal" class="absolute left-7 top-7 h-12 w-auto max-w-36 object-contain login-logo-image" />

          <div class="absolute bottom-10 left-10 right-10 max-w-md">
            <h1 class="text-5xl font-extrabold leading-none text-white">
              PRODUCCION FORESTAL EN TIEMPO REAL
            </h1>
            <p class="mt-5 text-sm font-semibold leading-relaxed text-white/85">
              Registra cargas, controla equipos y mantiene la información operativa sincronizada desde el campo.
            </p>
            <p class="mt-4 text-sm font-semibold text-white/90">
              Tus datos quedan listos para trabajar incluso cuando la conexión no acompaña.
            </p>
          </div>
        </aside>

        <main class="flex items-center justify-center bg-white px-12 py-10">
          <div class="w-full max-w-sm">
            <p class="text-xs font-extrabold uppercase text-primary-dark">BIENVENIDO DE VUELTA</p>
            <h2 class="mt-2 text-3xl font-extrabold leading-tight text-neutral-950">Acceso operativo</h2>
            <p class="mt-2 text-sm text-neutral-500">Ingresa con tu DNI y contraseña para continuar con el registro de producción.</p>

            <form @submit.prevent="handleLogin" class="mt-8 space-y-4">
              <div>
                <label for="desktop-dni" class="mb-1.5 block text-sm font-bold text-neutral-700">DNI</label>
                <input
                  id="desktop-dni"
                  v-model="dni"
                  type="text"
                  autocomplete="username"
                  inputmode="numeric"
                  maxlength="8"
                  placeholder="Ej: 12345678"
                  required
                  :disabled="authStore.loading"
                  class="h-12 w-full rounded-lg border border-neutral-300 bg-white px-4 text-sm text-neutral-900 placeholder:text-neutral-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:cursor-not-allowed disabled:bg-neutral-100"
                />
              </div>

              <div>
                <label for="desktop-password" class="mb-1.5 block text-sm font-bold text-neutral-700">Contraseña</label>
                <div class="relative">
                  <input
                    id="desktop-password"
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    autocomplete="current-password"
                    placeholder="Ingresa tu contraseña"
                    required
                    :disabled="authStore.loading"
                    class="h-12 w-full rounded-lg border border-neutral-300 bg-white px-4 pr-11 text-sm text-neutral-900 placeholder:text-neutral-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:cursor-not-allowed disabled:bg-neutral-100"
                  />
                  <button
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-neutral-400 transition-colors hover:text-neutral-700 focus:outline-none focus:ring-2 focus:ring-primary/20"
                    :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                    @click="showPassword = !showPassword"
                  >
                    <AppIcon :name="showPassword ? 'hide' : 'view'" size="sm" />
                  </button>
                </div>
              </div>

              <div
                v-if="authStore.error"
                :class="[
                  'flex items-start gap-2 rounded-lg p-3 text-sm',
                  errorCategory === 'offline'
                    ? 'bg-amber-100 text-amber-900'
                    : errorCategory === 'credentials'
                      ? 'bg-error-light text-error-dark'
                      : 'bg-error-light text-error-dark',
                ]"
                data-testid="login-error"
                role="alert"
              >
                <AppIcon
                  :name="errorCategory === 'offline' ? 'offline' : 'error'"
                  :class="['shrink-0', errorCategory === 'offline' ? 'text-amber-700 mt-0.5' : 'text-error mt-0.5']"
                />
                <div class="min-w-0 flex-1">
                  <p class="font-bold">
                    {{
                      errorCategory === 'offline'
                        ? 'Sin conexión'
                        : errorCategory === 'credentials'
                          ? 'Credenciales incorrectas'
                          : 'No se pudo validar el ingreso'
                    }}
                  </p>
                  <p class="mt-0.5 text-xs">{{ authStore.error }}</p>
                </div>
              </div>

              <div
                v-if="offlineNotice && !authStore.error"
                class="flex items-center gap-2 rounded-lg bg-amber-100 p-3 text-sm text-amber-900"
                role="status"
                aria-live="polite"
              >
                <AppIcon name="offline" class="shrink-0 text-amber-700" />
                <span>{{ offlineNotice }}</span>
              </div>

              <div
                v-if="syncMessage"
                class="flex items-center gap-2 rounded-lg bg-success-light p-3 text-sm text-success-dark"
              >
                <AppIcon name="success" class="shrink-0 text-success" />
                <span>{{ syncMessage }}</span>
              </div>

              <div class="grid gap-3 pt-1">
                <button
                  type="button"
                  @click="handleSync"
                  :disabled="authStore.loading || authStore.syncing"
                  class="flex h-12 w-full items-center justify-center gap-2 rounded-lg border border-primary bg-white px-4 text-sm font-bold text-primary transition-colors hover:bg-primary-light/20 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <AppIcon :name="authStore.syncing ? 'loading' : 'sync'" :class="authStore.syncing ? 'animate-spin' : ''" />
                  <span>{{ authStore.syncing ? 'Sincronizando...' : 'Sincronizar' }}</span>
                </button>

                <button
                  type="submit"
                  :disabled="authStore.loading"
                  class="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-primary-dark px-4 text-sm font-extrabold text-white transition-colors hover:bg-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <AppIcon v-if="authStore.loading" name="loading" class="animate-spin" />
                  <AppIcon v-else name="login" />
                  <span>{{ authStore.loading ? 'Ingresando...' : 'Ingresar' }}</span>
                </button>
              </div>
            </form>
          </div>
        </main>
      </section>
    </div>

    <!-- Mobile / Tablet -->
    <div class="flex min-h-[calc(100vh-3rem)] items-center justify-center lg:hidden">
      <section class="w-full max-w-md overflow-hidden rounded-[1.4rem] border-[8px] border-white bg-white shadow-2xl">
        <div class="relative min-h-72 overflow-hidden rounded-[0.9rem] p-7 text-white">
          <div class="absolute inset-0 bg-[linear-gradient(rgba(0,24,20,0.14),rgba(0,12,10,0.76))]"></div>
          <img src="/logo-forestal.png" alt="Logo Forestal" class="absolute left-5 top-5 h-11 w-auto max-w-32 object-contain login-logo-image" />
          <div class="absolute bottom-7 left-7 right-7">
            <h1 class="text-3xl font-extrabold leading-none">PRODUCCIÓN FORESTAL</h1>
            <p class="mt-3 text-sm font-semibold leading-relaxed text-white/85">
              Carga, sincroniza y consulta tu información operativa desde la PWA.
            </p>
          </div>
        </div>

        <div class="px-6 py-7">
          <p class="text-xs font-extrabold uppercase text-primary-dark">BIENVENIDO DE VUELTA</p>
          <h2 class="mt-2 text-2xl font-extrabold text-neutral-950">Acceso operativo</h2>
          <p class="mt-1 text-sm text-neutral-500">Ingresa con tu DNI y contraseña para continuar.</p>

          <form @submit.prevent="handleLogin" class="mt-6 space-y-4">
            <div>
              <label for="mobile-dni" class="mb-1.5 block text-sm font-bold text-neutral-700">DNI</label>
              <input
                id="mobile-dni"
                v-model="dni"
                type="text"
                autocomplete="username"
                inputmode="numeric"
                maxlength="8"
                placeholder="Ej: 12345678"
                required
                :disabled="authStore.loading"
                class="h-12 w-full rounded-lg border border-neutral-300 bg-white px-4 text-sm text-neutral-900 placeholder:text-neutral-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:cursor-not-allowed disabled:bg-neutral-100"
              />
            </div>

            <div>
              <label for="mobile-password" class="mb-1.5 block text-sm font-bold text-neutral-700">Contrasena</label>
              <div class="relative">
                <input
                  id="mobile-password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  autocomplete="current-password"
                  placeholder="Ingresa tu contrasena"
                  required
                  :disabled="authStore.loading"
                  class="h-12 w-full rounded-lg border border-neutral-300 bg-white px-4 pr-11 text-sm text-neutral-900 placeholder:text-neutral-400 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:cursor-not-allowed disabled:bg-neutral-100"
                />
                <button
                  type="button"
                  class="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-neutral-400 transition-colors hover:text-neutral-700 focus:outline-none focus:ring-2 focus:ring-primary/20"
                  :aria-label="showPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'"
                  @click="showPassword = !showPassword"
                >
                  <AppIcon :name="showPassword ? 'hide' : 'view'" size="sm" />
                </button>
              </div>
            </div>

            <div
              v-if="authStore.error"
              :class="[
                'flex items-start gap-2 rounded-lg p-3 text-sm',
                errorCategory === 'offline'
                  ? 'bg-amber-100 text-amber-900'
                  : 'bg-error-light text-error-dark',
              ]"
              data-testid="login-error"
              role="alert"
            >
              <AppIcon
                :name="errorCategory === 'offline' ? 'offline' : 'error'"
                :class="['shrink-0', errorCategory === 'offline' ? 'text-amber-700 mt-0.5' : 'text-error mt-0.5']"
              />
              <div class="min-w-0 flex-1">
                <p class="font-bold">
                  {{
                    errorCategory === 'offline'
                      ? 'Sin conexión'
                      : errorCategory === 'credentials'
                        ? 'Credenciales incorrectas'
                        : 'No se pudo validar el ingreso'
                  }}
                </p>
                <p class="mt-0.5 text-xs">{{ authStore.error }}</p>
              </div>
            </div>

            <div
              v-if="offlineNotice && !authStore.error"
              class="flex items-center gap-2 rounded-lg bg-amber-100 p-3 text-sm text-amber-900"
              role="status"
              aria-live="polite"
            >
              <AppIcon name="offline" class="shrink-0 text-amber-700" />
              <span>{{ offlineNotice }}</span>
            </div>

            <div
              v-if="syncMessage"
              class="flex items-center gap-2 rounded-lg bg-success-light p-3 text-sm text-success-dark"
            >
              <AppIcon name="success" class="shrink-0 text-success" />
              <span>{{ syncMessage }}</span>
            </div>

            <div class="grid gap-3">
              <button
                type="button"
                @click="handleSync"
                :disabled="authStore.loading || authStore.syncing"
                class="flex h-12 w-full items-center justify-center gap-2 rounded-lg border border-primary bg-white px-4 text-sm font-bold text-primary transition-colors hover:bg-primary-light/20 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <AppIcon :name="authStore.syncing ? 'loading' : 'sync'" :class="authStore.syncing ? 'animate-spin' : ''" />
                <span>{{ authStore.syncing ? 'Sincronizando...' : 'Sincronizar' }}</span>
              </button>

              <button
                type="submit"
                :disabled="authStore.loading"
                class="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-primary-dark px-4 text-sm font-extrabold text-white transition-colors hover:bg-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <AppIcon v-if="authStore.loading" name="loading" class="animate-spin" />
                <AppIcon v-else name="login" />
                <span>{{ authStore.loading ? 'Ingresando...' : 'Ingresar' }}</span>
              </button>
            </div>
          </form>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  useAuthStore,
  LOGIN_ERROR_BAD_CREDENTIALS,
  LOGIN_ERROR_NO_CONNECTION,
  LOGIN_ERROR_SERVER,
} from '@/stores/auth'
import { useConnectivityStore } from '@/stores/connectivity'
import AppIcon from '@/components/ui/AppIcon.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const connectivityStore = useConnectivityStore()

const dni = ref('')
const password = ref('')
const showPassword = ref(false)
const syncMessage = ref('')
const offlineNotice = ref('')

function isOffline() {
  return connectivityStore.isOffline
}

const errorCategory = computed(() => {
  const err = authStore.error
  if (!err) return null
  if (err === LOGIN_ERROR_NO_CONNECTION) return 'offline'
  if (err === LOGIN_ERROR_BAD_CREDENTIALS) return 'credentials'
  if (err === LOGIN_ERROR_SERVER) return 'server'
  return 'other'
})

onMounted(() => {
  // If the operator landed on /login with a cached offline session still valid,
  // send them straight to home. They are already authenticated, just without
  // network — they should not have to retype credentials.
  if (authStore.isAuthenticatedOffline) {
    offlineNotice.value =
      'Estás sin conexión, pero tu sesión guardada sigue activa. Entrando a la app.'
    router.replace({ name: 'home' })
    return
  }
  // If we are offline AND the cached session exists but is past the grace
  // period, surface a clear message so the operator understands why they
  // cannot enter.
  if (isOffline() && authStore.cachedSession && !authStore.isOfflineCacheValid()) {
    const age = authStore.offlineCacheAgeDays()
    offlineNotice.value = `Estás sin conexión y tu sesión guardada tiene ${age} días. Necesitamos validar contra el servidor para entrar.`
  } else if (isOffline() && authStore.initMode === 'offline-locked') {
    offlineNotice.value =
      'Estás sin conexión. No se puede validar contra el servidor ahora.'
  }
})

async function handleSync() {
  syncMessage.value = ''
  const result = await authStore.sincronizar()
  if (result.ok) {
    authStore.error = null
    syncMessage.value = `${result.data.message}. Personal activo: ${result.data.total_activos}`
  }
}

async function handleLogin() {
  syncMessage.value = ''
  offlineNotice.value = ''
  authStore.error = null
  const success = await authStore.login(dni.value, password.value)
  if (success) {
    authStore.clearOfflineCache()
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : null
    router.push(redirect ? { path: redirect } : { name: 'home' })
  }
}
</script>

<style scoped>
.login-shell {
  background-image:
    linear-gradient(rgba(0, 20, 16, 0.34), rgba(0, 12, 10, 0.62)),
    url("/background_johndeere.jpg");
  background-position: center;
  background-size: cover;
}

.login-logo-image {
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.55));
  mix-blend-mode: normal;
}
</style>
