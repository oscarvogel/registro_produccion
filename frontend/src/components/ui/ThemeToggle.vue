<template>
  <button
    v-if="variant === 'sidebar'"
    type="button"
    data-testid="theme-toggle"
    :class="sidebarButtonClass"
    :title="collapsed ? themeStatusLabel : undefined"
    :aria-label="themeToggleLabel"
    :aria-busy="isThemeTransitioning"
    :disabled="isThemeTransitioning"
    @click="toggleTheme"
  >
    <span :class="['flex min-w-0 items-center', collapsed ? 'md:justify-center md:gap-0 gap-3' : 'gap-3']">
      <span ref="iconTarget" class="relative flex h-5 w-5 shrink-0 items-center justify-center">
        <Transition name="theme-icon" mode="out-in">
          <AppIcon :key="isDark ? 'moon' : 'sun'" :name="isDark ? 'moon' : 'sun'" size="sm" />
        </Transition>
      </span>
      <span :class="['truncate', collapsed ? 'md:hidden' : '']">{{ themeStatusLabel }}</span>
    </span>
    <span
      :class="[
        'ml-2 h-5 w-9 rounded-full border border-[var(--app-nav-control-border)] p-0.5 transition-colors',
        isDark ? 'bg-[var(--app-nav-toggle-off-bg)]' : 'bg-secondary-light/80',
        collapsed ? 'md:hidden' : '',
      ]"
    >
      <span
        :class="[
          'block h-4 w-4 rounded-full bg-[var(--app-nav-text)] shadow-sm transition-transform duration-200',
          isDark ? 'translate-x-0' : 'translate-x-4',
        ]"
      ></span>
    </span>
  </button>

  <button
    v-else
    type="button"
    data-testid="theme-toggle"
    class="app-surface-muted flex min-h-12 w-full items-center justify-between gap-3 rounded-lg border px-3.5 py-2.5 text-left transition-all duration-150 ease-out hover:-translate-y-px hover:border-secondary/30 active:translate-y-0 active:scale-[0.99] disabled:cursor-wait"
    :aria-label="themeToggleLabel"
    :aria-busy="isThemeTransitioning"
    :disabled="isThemeTransitioning"
    @click="toggleTheme"
  >
    <span class="min-w-0">
      <span class="block text-sm font-extrabold text-neutral-800">{{ isDark ? 'Modo oscuro activo' : 'Modo claro activo' }}</span>
      <span class="block text-xs font-semibold text-neutral-500">{{ isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro' }}</span>
    </span>
    <span
      :class="[
        'h-7 w-12 shrink-0 rounded-full border p-0.5 transition-colors',
        isDark ? 'border-primary/30 bg-primary-dark' : 'border-secondary/20 bg-secondary-light',
      ]"
    >
      <span
        ref="settingsIconTarget"
        :class="[
          'app-card flex h-6 w-6 items-center justify-center rounded-full text-info-dark shadow-sm transition-transform duration-200',
          isDark ? 'translate-x-0' : 'translate-x-5',
        ]"
      >
        <Transition name="theme-icon" mode="out-in">
          <AppIcon :key="isDark ? 'moon' : 'sun'" :name="isDark ? 'moon' : 'sun'" size="xs" />
        </Transition>
      </span>
    </span>
  </button>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { animateThemeIcon } from '@/config/gsap'
import { useTheme } from '@/composables/useTheme'

const props = defineProps({
  variant: { type: String, default: 'sidebar' },
  collapsed: { type: Boolean, default: false },
})

const iconTarget = ref(null)
const settingsIconTarget = ref(null)
const { isDark, toggleTheme, isThemeTransitioning } = useTheme()
let activeAnimations = []

const themeToggleLabel = computed(() => (isDark.value ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'))
const themeStatusLabel = computed(() => (isDark.value ? 'Modo oscuro' : 'Modo claro'))
const sidebarButtonClass = computed(() => [
  'relative flex min-h-11 w-full items-center justify-between gap-2 rounded-lg border py-2 text-sm font-semibold transition-all duration-150 ease-out hover:-translate-y-px active:translate-y-0 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 disabled:cursor-wait disabled:hover:translate-y-0',
  props.collapsed ? 'md:justify-center md:px-2 justify-between px-3' : 'justify-between px-3',
  'border-transparent bg-transparent text-[var(--app-nav-text-muted)] hover:border-[var(--app-nav-border)] hover:bg-[var(--app-nav-surface)] hover:text-[var(--app-nav-text)]',
])

watch(isDark, async (_nextTheme, oldTheme) => {
  if (oldTheme === undefined) return

  await nextTick()
  activeAnimations.forEach((animation) => animation?.kill?.())
  activeAnimations = [
    animateThemeIcon(iconTarget.value),
    animateThemeIcon(settingsIconTarget.value),
  ].filter(Boolean)
})

onBeforeUnmount(() => {
  activeAnimations.forEach((animation) => animation?.kill?.())
  activeAnimations = []
})
</script>
