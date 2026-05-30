<template>
  <div class="min-h-screen flex items-center justify-center bg-neutral-100 px-4">
    <div class="w-full max-w-md">
      <!-- Logo / Header -->
      <div class="text-center mb-8">
        <div
          class="mx-auto w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-4"
        >
          <AppIcon name="personnel" size="xl" class="text-white" />
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
              autocomplete="username"
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
                autocomplete="current-password"
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
                <AppIcon :name="showPassword ? 'hide' : 'view'" />
              </button>
            </div>
          </div>

          <!-- Error message -->
          <div
            v-if="authStore.error"
            class="flex items-center gap-2 p-3 bg-error-light text-error-dark rounded-lg text-sm"
          >
            <AppIcon name="error" class="text-error shrink-0" />
            <span>{{ authStore.error }}</span>
          </div>

          <div
            v-if="syncMessage"
            class="flex items-center gap-2 p-3 bg-success-light text-success-dark rounded-lg text-sm"
          >
            <AppIcon name="success" class="text-success shrink-0" />
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
            <AppIcon :name="authStore.syncing ? 'loading' : 'sync'" :class="authStore.syncing ? 'animate-spin' : ''" />
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
            <AppIcon v-if="authStore.loading" name="loading" class="animate-spin" />
            <AppIcon v-else name="login" />
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
import AppIcon from '@/components/ui/AppIcon.vue'

const router = useRouter()
const authStore = useAuthStore()

const dni = ref('')
const password = ref('')
const showPassword = ref(false)
const syncMessage = ref('')

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
  const success = await authStore.login(dni.value, password.value)
  if (success) {
    router.push({ name: 'home' })
  }
}
</script>
