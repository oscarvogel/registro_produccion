<template>
  <div class="min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center px-4 py-8 bg-neutral-100">
    <!-- Logo placeholder -->
    <div class="mb-6">
      <img
        src="/logo-forestal.png"
        alt="Forestal Garuhapé"
        class="h-28 w-auto object-contain"
        @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'"
      />
      <!-- Fallback if image not found -->
      <div
        class="hidden h-28 w-28 bg-primary rounded-2xl items-center justify-center"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-14 h-14 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17 10.5V7a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-3.5" />
          <path d="M12 12H3" />
          <path d="M21 12h-4" />
          <circle cx="7.5" cy="17.5" r="2.5" />
          <circle cx="17.5" cy="17.5" r="2.5" />
        </svg>
      </div>
    </div>

    <!-- Titulo -->
    <h2 class="text-2xl font-bold text-neutral-900 mb-1">Registro de Producción</h2>
    <p class="text-neutral-500 mb-2">{{ greeting }}</p>

    <!-- Estado -->
    <div class="flex items-center gap-2 mb-10">
      <span class="w-2.5 h-2.5 rounded-full bg-success animate-pulse"></span>
      <span class="text-sm text-neutral-500">En línea</span>
    </div>

    <!-- Botón principal -->
    <button
      @click="$router.push({ name: 'produccion' })"
      class="w-full max-w-sm py-4 px-8 bg-gradient-to-r from-primary to-secondary
             text-white text-lg font-bold rounded-2xl shadow-lg
             hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]
             transition-all duration-200 flex items-center justify-center gap-3"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="6 3 20 12 6 21 6 3" />
      </svg>
      CARGA DE PRODUCCIÓN
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const greeting = computed(() => {
  const name = authStore.userName
  return name ? `Bienvenido, ${name}` : 'Bienvenido'
})
</script>
