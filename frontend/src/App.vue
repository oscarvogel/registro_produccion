<template>
  <div id="app" class="min-h-screen bg-neutral-100">
    <!-- Navbar only when authenticated -->
    <nav
      v-if="authStore.isAuthenticated"
      class="bg-white border-b border-neutral-200 shadow-sm"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-14">
          <div class="flex items-center gap-6">
            <span class="text-primary-dark font-bold text-lg">Registro Producción</span>
            <div class="flex gap-1">
              <router-link
                to="/"
                class="px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                active-class="!bg-primary-light/20 !text-primary-dark"
              >
                Inicio
              </router-link>
              <router-link
                to="/items"
                class="px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                active-class="!bg-primary-light/20 !text-primary-dark"
              >
                Items
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

    <router-view />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>
