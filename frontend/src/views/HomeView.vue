<template>
  <div class="min-h-[calc(100vh-8.5rem)] md:min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center px-4 py-7 bg-neutral-100">
    <div class="w-full max-w-md flex flex-col items-center text-center">
      <div class="mb-8 h-[11rem] w-[11rem] rounded-[1.9rem] bg-primary shadow-[0_10px_28px_rgba(61,147,93,0.3)] flex items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-14 h-14 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 7a2 2 0 0 1 2-2h9l3 4h2a2 2 0 0 1 2 2v4" />
          <path d="M16 17h1a2 2 0 0 0 2-2" />
          <path d="M3 17h8" />
          <circle cx="7" cy="17" r="2" />
          <circle cx="16" cy="17" r="2" />
        </svg>
      </div>

      <h1 class="text-[2.8rem] md:text-[3rem] leading-tight font-extrabold text-neutral-950 mb-2">Registro de Producción</h1>
      <p class="text-neutral-600 text-[1.9rem] md:text-[2rem] leading-tight mb-3">
        Bienvenido,
        <span class="text-neutral-950 font-bold uppercase">{{ authStore.userName }}</span>
      </p>

      <div class="flex items-center gap-2 mb-10">
        <span class="w-2.5 h-2.5 rounded-full bg-success"></span>
        <span class="text-success text-[1.35rem] font-medium">En línea</span>
      </div>

      <button
        @click="$router.push({ name: 'produccion' })"
        class="w-full py-4 px-7 bg-gradient-to-r from-primary to-secondary-dark text-white text-[1.55rem] md:text-[2rem] font-extrabold tracking-wide rounded-[1.5rem] shadow-[0_10px_20px_rgba(61,147,93,0.3)] active:scale-[0.99] transition-transform duration-150 flex items-center justify-center gap-3"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 md:w-8 md:h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="6 3 20 12 6 21 6 3" />
        </svg>
        CARGA DE PRODUCCIÓN
      </button>

      <button
        v-if="authStore.user?.encargado === 1"
        @click="$router.push({ name: 'dashboard' })"
        class="w-full mt-4 py-3.5 px-7 bg-white border-2 border-primary text-primary text-[1.4rem] md:text-[1.8rem] font-extrabold tracking-wide rounded-[1.5rem] active:scale-[0.99] transition-all duration-150 flex items-center justify-center gap-3 hover:bg-primary hover:text-white"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" class="w-6 h-6 md:w-7 md:h-7">
          <rect x="3" y="3" width="7" height="7" rx="1"/>
          <rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/>
          <rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>
        VER DASHBOARD
      </button>

      <p class="mt-8 text-neutral-400 text-[1.2rem] md:text-[1.7rem]">Pulse para iniciar un nuevo registro</p>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>
