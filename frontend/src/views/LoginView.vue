<template>
  <div class="min-h-screen flex items-center justify-center bg-neutral-100 px-4">
    <div class="w-full max-w-md">
      <!-- Logo / Header -->
      <div class="text-center mb-8">
        <div
          class="mx-auto w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-4"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-8 h-8 text-white"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-neutral-900">Registro de Producción</h1>
        <p class="text-neutral-500 mt-1">Ingresá con tu DNI y contraseña</p>
      </div>

      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-lg p-8">
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- DNI -->
          <div>
            <label for="dni" class="block text-sm font-medium text-neutral-700 mb-1">
              DNI
            </label>
            <input
              id="dni"
              v-model="dni"
              type="text"
              inputmode="numeric"
              maxlength="8"
              placeholder="Ej: 12345678"
              required
              :disabled="authStore.loading"
              class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                     placeholder:text-neutral-400
                     focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
                     disabled:bg-neutral-100 disabled:cursor-not-allowed
                     transition-colors"
            />
          </div>

          <!-- Password -->
          <div>
            <label
              for="password"
              class="block text-sm font-medium text-neutral-700 mb-1"
            >
              Contraseña
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Ingresá tu contraseña"
                required
                :disabled="authStore.loading"
                class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                       placeholder:text-neutral-400
                       focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
                       disabled:bg-neutral-100 disabled:cursor-not-allowed
                       transition-colors pr-11"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 transition-colors"
                tabindex="-1"
              >
                <svg
                  v-if="!showPassword"
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-5 h-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-5 h-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49" />
                  <path d="M14.084 14.158a3 3 0 0 1-4.242-4.242" />
                  <path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143" />
                  <path d="m2 2 20 20" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Error message -->
          <div
            v-if="authStore.error"
            class="flex items-center gap-2 p-3 bg-error-light text-error-dark rounded-lg text-sm"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 text-error shrink-0"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" x2="12" y1="8" y2="12" />
              <line x1="12" x2="12.01" y1="16" y2="16" />
            </svg>
            <span>{{ authStore.error }}</span>
          </div>

          <div
            v-if="syncMessage"
            class="flex items-center gap-2 p-3 bg-success-light text-success-dark rounded-lg text-sm"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 text-success shrink-0"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M20 6 9 17l-5-5" />
            </svg>
            <span>{{ syncMessage }}</span>
          </div>

          <button
            type="button"
            @click="handleSync"
            :disabled="authStore.loading || authStore.syncing"
            class="w-full py-2.5 px-4 border border-primary text-primary font-medium
                   rounded-lg transition-colors duration-200
                   hover:bg-primary-light/20
                   focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
                   disabled:opacity-60 disabled:cursor-not-allowed
                   flex items-center justify-center gap-2"
          >
            <svg
              v-if="authStore.syncing"
              class="w-5 h-5 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
              <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
              <path d="M3 16h4v4" />
              <path d="M17 4h4v4" />
            </svg>
            <span>{{ authStore.syncing ? 'Sincronizando...' : 'Sincronizar' }}</span>
          </button>

          <!-- Submit button -->
          <button
            type="submit"
            :disabled="authStore.loading"
            class="w-full py-2.5 px-4 bg-primary hover:bg-primary-dark text-white font-medium
                   rounded-lg transition-colors duration-200
                   focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
                   disabled:opacity-60 disabled:cursor-not-allowed
                   flex items-center justify-center gap-2"
          >
            <svg
              v-if="authStore.loading"
              class="w-5 h-5 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            <span>{{ authStore.loading ? 'Ingresando...' : 'Ingresar' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const dni = ref('')
const password = ref('')
const showPassword = ref(false)
const syncMessage = ref('')

async function handleSync() {
  syncMessage.value = ''
  if (!dni.value?.trim()) {
    authStore.error = 'Ingresá tu DNI para sincronizar'
    return
  }
  const result = await authStore.sincronizar(dni.value.trim())
  if (result.ok) {
    authStore.error = null
    syncMessage.value = `Datos sincronizados: ${result.user.nombre}`
  }
}

async function handleLogin() {
  syncMessage.value = ''
  const success = await authStore.login(dni.value, password.value)
  if (success) {
    router.push({ name: 'home' })
  }
}
</script>
