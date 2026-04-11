<template>
  <div class="min-h-[calc(100vh-8.5rem)] md:min-h-[calc(100vh-3.5rem)] flex flex-col items-center pt-8 pb-6 px-5 bg-neutral-100">
    <div class="w-full max-w-md flex flex-col items-center">

      <!-- Online badge -->
      <div class="flex items-center gap-2 mb-5 bg-white rounded-full px-5 py-2 shadow-sm border border-neutral-200">
        <span class="w-2 h-2 rounded-full bg-success"></span>
        <span class="text-success text-[1.2rem] font-semibold uppercase tracking-widest">En línea</span>
      </div>

      <!-- Username -->
      <h1 class="text-[2.6rem] md:text-[3rem] font-extrabold text-primary-dark uppercase text-center leading-tight mb-7">
        {{ authStore.userName }}
      </h1>

      <!-- Stacked card visual -->
      <div class="w-full mb-7 relative px-4">
        <!-- Back card (decorative) -->
        <div class="absolute left-1 right-1 top-5 bottom-0 bg-primary-dark rounded-[1.6rem] z-0"></div>
        <!-- Front white card -->
        <div class="relative z-10 bg-white rounded-[1.6rem] shadow-[0_4px_24px_rgba(0,0,0,0.10)] py-10 flex justify-center items-center">
          <div class="w-28 h-28 rounded-[1.6rem] bg-primary-light/30 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-14 h-14 text-primary-dark" viewBox="0 0 24 24" fill="currentColor">
              <path d="M1 3h15v13H1zM16 8h4l3 3v5h-7V8z"/>
              <circle cx="5.5" cy="18.5" r="2.5"/>
              <circle cx="18.5" cy="18.5" r="2.5"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- CTA — Carga de producción -->
      <button
        @click="$router.push({ name: 'produccion' })"
        class="w-full bg-primary-dark text-white rounded-[1.5rem] px-6 py-4 flex items-center justify-between shadow-[0_8px_24px_rgba(20,61,35,0.35)] active:scale-[0.99] transition-transform duration-150 mb-4"
      >
        <div class="flex flex-col items-start text-left">
          <span class="text-[1.1rem] font-medium tracking-[0.18em] uppercase text-white/70 mb-0.5">Iniciar Tarea</span>
          <span class="text-[1.6rem] font-extrabold tracking-wide uppercase leading-tight">Carga de Producción</span>
        </div>
        <div class="flex-shrink-0 ml-4 w-12 h-12 rounded-[0.9rem] bg-white/15 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="6 3 20 12 6 21 6 3" />
          </svg>
        </div>
      </button>

      <!-- Secondary actions -->
      <div class="grid grid-cols-2 gap-4 w-full">
        <!-- Mis registros -->
        <button
          @click="$router.push({ name: 'mis-registros' })"
          class="bg-white rounded-[1.4rem] py-6 px-4 flex flex-col items-center gap-3 shadow-sm border border-neutral-200 active:scale-[0.98] transition-transform duration-150 hover:border-primary/40"
        >
          <div class="w-12 h-12 rounded-[0.9rem] bg-primary-light/25 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 text-primary-dark">
              <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
            </svg>
          </div>
          <span class="text-[1.2rem] font-extrabold text-neutral-700 tracking-wide uppercase">Mis Registros</span>
        </button>

        <!-- Ver dashboard -->
        <button
          @click="$router.push({ name: 'dashboard' })"
          class="bg-white rounded-[1.4rem] py-6 px-4 flex flex-col items-center gap-3 shadow-sm border border-neutral-200 active:scale-[0.98] transition-transform duration-150 hover:border-primary/40"
        >
          <div class="w-12 h-12 rounded-[0.9rem] bg-primary-light/25 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 text-primary-dark">
              <rect x="3" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="3" width="7" height="7" rx="1"/>
              <rect x="3" y="14" width="7" height="7" rx="1"/>
              <rect x="14" y="14" width="7" height="7" rx="1"/>
            </svg>
          </div>
          <span class="text-[1.2rem] font-extrabold text-neutral-700 tracking-wide uppercase">Ver Dashboard</span>
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>
