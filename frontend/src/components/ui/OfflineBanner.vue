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
      <span>{{ label }}</span>
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
})

const connectivity = useConnectivityStore()

const visible = computed(() => connectivity.isOffline)

const bannerClasses = computed(() => {
  // Background depends on what is wrong: pure offline (amber) vs backend
  // unreachable but online (red). Both mean "no sincronization right now".
  if (!connectivity.isOnline) {
    return 'bg-amber-500 text-white'
  }
  return 'bg-error text-white'
})

const icon = computed(() => 'offline')

const label = computed(() => {
  if (props.message) return props.message
  if (!connectivity.isOnline) {
    return 'Sin conexión - Los registros se guardarán localmente y se sincronizarán al reconectar'
  }
  return 'Servidor no disponible - Los registros se guardarán localmente'
})
</script>
