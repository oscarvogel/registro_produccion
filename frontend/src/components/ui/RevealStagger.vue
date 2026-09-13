<template>
  <component
    :is="as"
    ref="root"
    v-bind="passthroughAttrs"
    :class="rootClass"
    :style="rootStyle"
  >
    <slot />
  </component>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, useAttrs } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  as: { type: [String, Object], default: 'div' },
  stagger: { type: Number, default: 55 },
  once: { type: Boolean, default: true },
})

const root = ref(null)
const visible = ref(false)
const attrs = useAttrs()
let observer = null

const passthroughAttrs = computed(() => {
  const { class: _class, style: _style, ...rest } = attrs
  return rest
})

const rootClass = computed(() => [
  'app-reveal-stagger',
  visible.value ? 'app-reveal-stagger--visible' : '',
  attrs.class,
])

const rootStyle = computed(() => [
  attrs.style,
  { '--app-motion-stagger': `${props.stagger}ms` },
])

function show() {
  visible.value = true
  if (props.once) observer?.unobserve(root.value)
}

onMounted(() => {
  const reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reducedMotion || typeof IntersectionObserver === 'undefined') {
    show()
    return
  }

  observer = new IntersectionObserver(([entry]) => {
    if (entry?.isIntersecting) show()
  }, { threshold: 0.08, rootMargin: '0px 0px -6% 0px' })

  if (root.value) observer.observe(root.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
  observer = null
})
</script>
