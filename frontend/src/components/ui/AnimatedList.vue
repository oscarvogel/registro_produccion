<template>
  <TransitionGroup
    v-bind="passthroughAttrs"
    :tag="props.tag"
    :name="props.name"
    :appear="props.appear"
    :class="listClass"
    :style="listStyle"
  >
    <slot />
  </TransitionGroup>
</template>

<script setup>
import { computed, useAttrs } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  tag: { type: [String, Object], default: 'div' },
  name: { type: String, default: 'app-animated-list' },
  stagger: { type: Number, default: 45 },
  appear: { type: Boolean, default: true },
})

const attrs = useAttrs()
const passthroughAttrs = computed(() => {
  const { class: _class, style: _style, ...rest } = attrs
  return rest
})
const listClass = computed(() => ['app-animated-list', attrs.class])
const listStyle = computed(() => [attrs.style, { '--app-list-stagger': `${props.stagger}ms` }])
</script>
