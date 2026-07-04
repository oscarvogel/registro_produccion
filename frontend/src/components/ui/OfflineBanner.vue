<template>
  <Transition name="status-slide">
    <div
      v-if="visible"
      :class="[
        'fixed left-0 right-0 top-0 z-[60] flex items-center justify-center gap-2 px-3 py-1.5 text-xs font-semibold',
        bannerClasses,
      ]"
      role="status"
      aria-live="polite"
      data-testid="offline-banner"
    >
      <AppIcon :name="icon" size="sm" :stroke-width="2.5" class="shrink-0" />
      <span class="truncate">{{ label }}</span>
      <span
        v-if="pendingCount > 0"
        class="ml-1 rounded bg-white/20 px-1.5"
        data-testid="offline-banner-pending"
      >
        {{ pendingCount }} pendiente{{ pendingCount !== 1 ? 's' : '' }}
      </span>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { useConnectivityStore } from '@/stores/connectivity'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps({
  // Optional explicit override for the label/message (rare).
  message: { type: String, default: '' },
  // Optional pending count to display (used for production records).
  pendingCount: { type: Number, default: 0 },
  // Optional flag: when true, the operator already has a valid cached session
  // on this device, so we can drop the "first time" caveat. Pass `false` when
  // the operator lands offline without ever having signed in here — the banner
  // then explains why they still have to type credentials once with internet.
  hasCachedSession: { type: Boolean, default: true },
})

const connectivity = useConnectivityStore()

const visible = computed(() => connectivity.isOfflineOrBackendDown)

const bannerClasses = computed(() => {
  // Background depends on what is wrong: pure offline (amber) vs backend
  // unreachable but online (red). Both mean "no sincronization right now".
  if (connectivity.isOffline) {
    return 'bg-amber-500 text-white'
  }
  return 'bg-error text-white'
})

const icon = computed(() => 'offline')

const label = computed(() => {
  if (props.message) return props.message
  if (connectivity.isOffline) {
    if (props.hasCachedSession) {
      return 'Sin conexión - los registros se guardan localmente y se sincronizan al reconectar'
    }
    return 'Sin conexión - primera vez: necesitás iniciar sesión una vez con internet para guardar tu sesión hasta 14 días'
  }
  // Online but backend unhealthy — keep this short so it fits on mobile.
  return 'Servidor no disponible - los registros se guardarán localmente'
})
</script>
