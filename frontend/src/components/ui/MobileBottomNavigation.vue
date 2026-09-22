<template>
  <nav
    class="app-mobile-bottom-navigation fixed inset-x-0 bottom-0 z-30 md:hidden"
    aria-label="Navegación móvil"
  >
    <div class="app-mobile-bottom-navigation__surface mx-auto grid w-full max-w-2xl grid-cols-5 items-stretch">
      <RouterLink
        v-for="item in items"
        :key="item.key"
        :to="item.to"
        :aria-label="itemAccessibleName(item)"
        :aria-current="item.key === activeKey ? 'page' : undefined"
        :title="item.accessibleLabel || item.label"
        :class="[
          'app-mobile-bottom-navigation__item group flex w-full min-w-0 flex-col items-center justify-center gap-0.5 rounded-xl px-0.5 text-[var(--app-nav-text-muted)] transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--app-nav-accent)] focus-visible:ring-inset',
          item.key === activeKey ? 'is-active text-[var(--app-nav-text)]' : 'hover:text-[var(--app-nav-text)]',
        ]"
      >
        <span class="app-mobile-bottom-navigation__icon-shell relative flex h-10 w-10 items-center justify-center rounded-full transition-[transform,background-color,box-shadow] duration-200">
          <NavigationIcon :name="item.icon" :theme="theme" size="md" />
          <span
            v-if="Number(item.badge || 0) > 0"
            class="absolute -right-0.5 -top-0.5 flex min-h-4 min-w-4 items-center justify-center rounded-full bg-warning px-1 text-[9px] font-extrabold leading-none text-on-warning ring-2 ring-[var(--app-nav-bg)]"
            aria-hidden="true"
          >
            {{ item.badge > 99 ? '99+' : item.badge }}
          </span>
        </span>
        <span class="max-w-full truncate text-[0.625rem] font-semibold leading-3 transition-[margin] duration-200">{{ item.mobileLabel || item.label }}</span>
      </RouterLink>

      <button
        ref="moreButton"
        type="button"
        class="app-mobile-bottom-navigation__item group flex w-full min-w-0 flex-col items-center justify-center gap-0.5 rounded-xl px-0.5 text-[var(--app-nav-text-muted)] transition-colors duration-150 hover:text-[var(--app-nav-text)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--app-nav-accent)] focus-visible:ring-inset"
        :aria-label="moreExpanded ? 'Cerrar más opciones' : 'Abrir más opciones'"
        aria-controls="app-mobile-more-panel"
        :aria-expanded="moreExpanded"
        :class="moreActive || moreExpanded ? 'is-active text-[var(--app-nav-text)]' : ''"
        @click="$emit('open-more', $event.currentTarget)"
      >
        <span class="app-mobile-bottom-navigation__icon-shell flex h-10 w-10 items-center justify-center rounded-full transition-[transform,background-color,box-shadow] duration-200">
          <AppIcon name="menu" size="sm" />
        </span>
        <span class="text-[0.625rem] font-semibold leading-3 transition-[margin] duration-200">Más</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import NavigationIcon from '@/components/ui/NavigationIcon.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

defineProps({
  items: { type: Array, default: () => [] },
  activeKey: { type: String, default: '' },
  moreActive: { type: Boolean, default: false },
  moreExpanded: { type: Boolean, default: false },
  theme: { type: String, default: 'dark' },
})

defineEmits(['open-more'])

const moreButton = ref(null)

function itemAccessibleName(item) {
  const label = item.accessibleLabel || item.label
  const count = Number(item.badge || 0)
  return count > 0 ? `${label}, ${count} pendientes` : label
}

defineExpose({ moreButton })
</script>
