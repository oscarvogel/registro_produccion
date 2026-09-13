<template>
  <span>{{ displayValue }}</span>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  value: { type: [Number, String], default: 0 },
  from: { type: Number, default: null },
  duration: { type: Number, default: 450 },
  format: { type: Function, default: (value) => String(value) },
})

const displayValue = ref(formatValue(props.from ?? props.value))
let animationFrame = null
let mounted = false
let reducedMotion = false

function numericValue(value) {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : null
}

function formatValue(value) {
  return props.format(value)
}

function cancelAnimation() {
  if (animationFrame !== null) {
    cancelAnimationFrame(animationFrame)
    animationFrame = null
  }
}

function setValue(value) {
  displayValue.value = formatValue(value)
}

function animateTo(target, start) {
  cancelAnimation()

  if (reducedMotion || props.duration <= 0 || target === start) {
    setValue(target)
    return
  }

  const startedAt = performance.now()
  const step = (now) => {
    const progress = Math.min((now - startedAt) / props.duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    setValue(start + (target - start) * eased)

    if (progress < 1) {
      animationFrame = requestAnimationFrame(step)
    } else {
      animationFrame = null
      setValue(target)
    }
  }

  animationFrame = requestAnimationFrame(step)
}

onMounted(() => {
  mounted = true
  reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches || false

  const target = numericValue(props.value)
  if (props.from !== null && target !== null) {
    animateTo(target, props.from)
  } else {
    setValue(props.value)
  }
})

watch(() => props.value, (nextValue, previousValue) => {
  if (!mounted) return

  const target = numericValue(nextValue)
  const start = numericValue(previousValue)
  if (target === null || start === null) {
    cancelAnimation()
    setValue(nextValue)
    return
  }

  animateTo(target, start)
})

onBeforeUnmount(cancelAnimation)
</script>
