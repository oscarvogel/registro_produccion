<template>
  <Transition name="mobile-more">
    <section
      v-if="open"
      id="app-mobile-more-panel"
      ref="panelElement"
      class="app-mobile-more-panel"
      role="region"
      aria-label="Más opciones"
    >
      <div class="mb-3 flex items-center justify-between gap-3">
        <h2 class="text-sm font-extrabold text-[var(--app-nav-text)]">Más opciones</h2>
        <button
          type="button"
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-[var(--app-nav-text-muted)] transition-colors hover:bg-[var(--app-nav-surface)] hover:text-[var(--app-nav-text)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--app-nav-accent)]"
          aria-label="Cerrar más opciones"
          @click="emit('close')"
        >
          <AppIcon name="close" size="sm" />
        </button>
      </div>

      <nav aria-label="Destinos adicionales" class="space-y-4">
        <section v-for="group in groups" :key="group.key">
          <h3 class="mb-2 text-[0.65rem] font-bold uppercase tracking-[0.12em] text-[var(--app-nav-text-soft)]">
            {{ group.label }}
          </h3>
          <div class="grid grid-cols-2 gap-2">
            <RouterLink
              v-for="item in group.items"
              :key="item.key"
              :to="item.to"
              :aria-label="itemAccessibleName(item)"
              :aria-current="item.key === activeKey ? 'page' : undefined"
              :class="[
                'flex min-h-12 min-w-0 items-center gap-2 rounded-lg border px-2.5 py-2 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--app-nav-accent)]',
                item.key === activeKey
                  ? 'border-[var(--app-nav-active-border)] bg-[var(--app-nav-active-bg)] text-[var(--app-nav-text)]'
                  : 'border-[var(--app-nav-border)] bg-[var(--app-nav-surface)] text-[var(--app-nav-text-muted)] hover:text-[var(--app-nav-text)]',
              ]"
              @click="emit('navigate')"
            >
              <NavigationIcon :name="item.icon" :theme="theme" size="sm" class="shrink-0" />
              <span class="min-w-0 flex-1 leading-tight">{{ item.label }}</span>
              <span
                v-if="Number(item.badge || 0) > 0"
                class="flex h-5 min-w-5 shrink-0 items-center justify-center rounded-full bg-warning px-1 text-[0.625rem] font-extrabold leading-none text-on-warning"
                aria-hidden="true"
              >
                {{ item.badge > 99 ? '99+' : item.badge }}
              </span>
            </RouterLink>
          </div>
        </section>
      </nav>

      <slot name="utilities" />
    </section>
  </Transition>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import NavigationIcon from '@/components/ui/NavigationIcon.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  groups: { type: Array, default: () => [] },
  activeKey: { type: String, default: '' },
  theme: { type: String, default: 'dark' },
  triggerElement: { type: Object, default: null },
})

const emit = defineEmits(['close', 'navigate'])
const panelElement = ref(null)

function itemAccessibleName(item) {
  const label = item.accessibleLabel || item.label
  const count = Number(item.badge || 0)
  return count > 0 ? `${label}, ${count} pendientes` : label
}

function handleOutsideClick(event) {
  if (!props.open) return
  if (panelElement.value?.contains(event.target) || props.triggerElement?.contains(event.target)) return
  emit('close')
}

function handleEscape(event) {
  if (!props.open || event.key !== 'Escape') return
  event.preventDefault()
  emit('close')
  props.triggerElement?.focus()
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  document.addEventListener('keydown', handleEscape)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  document.removeEventListener('keydown', handleEscape)
})

watch(() => props.open, (open, wasOpen) => {
  if (!open && wasOpen && panelElement.value?.contains(document.activeElement)) {
    props.triggerElement?.focus()
  }
})
</script>
