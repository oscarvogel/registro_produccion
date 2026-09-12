<template>
  <img
    :src="source"
    :width="sizeMap[size] || sizeMap.sm"
    :height="sizeMap[size] || sizeMap.sm"
    alt=""
    aria-hidden="true"
    draggable="false"
    v-bind="$attrs"
  />
</template>

<script setup>
import { computed } from 'vue'
import darkAdmin from '@/assets/navigation-icons/dark/admin.svg'
import darkAnalysis from '@/assets/navigation-icons/dark/analysis.svg'
import darkDashboard from '@/assets/navigation-icons/dark/dashboard.svg'
import darkFuelAdd from '@/assets/navigation-icons/dark/fuel-add.svg'
import darkFuel from '@/assets/navigation-icons/dark/fuel.svg'
import darkHome from '@/assets/navigation-icons/dark/home.svg'
import darkLogout from '@/assets/navigation-icons/dark/logout.svg'
import darkManual from '@/assets/navigation-icons/dark/manual.svg'
import darkPending from '@/assets/navigation-icons/dark/pending.svg'
import darkProductionAdd from '@/assets/navigation-icons/dark/production-add.svg'
import darkProduction from '@/assets/navigation-icons/dark/production.svg'
import darkRecords from '@/assets/navigation-icons/dark/records.svg'
import darkSettings from '@/assets/navigation-icons/dark/settings.svg'
import darkTracking from '@/assets/navigation-icons/dark/tracking.svg'
import lightAdmin from '@/assets/navigation-icons/light/admin.svg'
import lightAnalysis from '@/assets/navigation-icons/light/analysis.svg'
import lightDashboard from '@/assets/navigation-icons/light/dashboard.svg'
import lightFuelAdd from '@/assets/navigation-icons/light/fuel-add.svg'
import lightFuel from '@/assets/navigation-icons/light/fuel.svg'
import lightHome from '@/assets/navigation-icons/light/home.svg'
import lightLogout from '@/assets/navigation-icons/light/logout.svg'
import lightManual from '@/assets/navigation-icons/light/manual.svg'
import lightPending from '@/assets/navigation-icons/light/pending.svg'
import lightProductionAdd from '@/assets/navigation-icons/light/production-add.svg'
import lightProduction from '@/assets/navigation-icons/light/production.svg'
import lightRecords from '@/assets/navigation-icons/light/records.svg'
import lightSettings from '@/assets/navigation-icons/light/settings.svg'
import lightTracking from '@/assets/navigation-icons/light/tracking.svg'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  name: { type: String, default: 'home' },
  theme: { type: String, default: 'dark' },
  size: { type: String, default: 'sm' },
})

const sizeMap = {
  xs: 16,
  sm: 20,
  md: 24,
}

const iconSets = {
  dark: {
    admin: darkAdmin,
    analysis: darkAnalysis,
    dashboard: darkDashboard,
    'fuel-add': darkFuelAdd,
    fuel: darkFuel,
    home: darkHome,
    logout: darkLogout,
    manual: darkManual,
    pending: darkPending,
    'production-add': darkProductionAdd,
    production: darkProduction,
    records: darkRecords,
    settings: darkSettings,
    tracking: darkTracking,
  },
  light: {
    admin: lightAdmin,
    analysis: lightAnalysis,
    dashboard: lightDashboard,
    'fuel-add': lightFuelAdd,
    fuel: lightFuel,
    home: lightHome,
    logout: lightLogout,
    manual: lightManual,
    pending: lightPending,
    'production-add': lightProductionAdd,
    production: lightProduction,
    records: lightRecords,
    settings: lightSettings,
    tracking: lightTracking,
  },
}

const source = computed(() => {
  const set = iconSets[props.theme] || iconSets.dark
  return set[props.name] || set.home
})
</script>
