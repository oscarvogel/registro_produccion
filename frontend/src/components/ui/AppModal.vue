<template>
  <Teleport to="body">
    <Transition name="modal-backdrop">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-3 backdrop-blur-sm sm:p-4"
        @click.self="close"
        @keydown.esc.stop.prevent="close"
      >
        <div
          ref="dialogRef"
          v-motion-pop
          class="app-card-glass w-full max-w-2xl rounded-xl"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          :aria-describedby="description ? descriptionId : undefined"
          tabindex="-1"
        >
          <div class="flex items-start justify-between gap-4 border-b border-neutral-200 px-4 py-3">
            <div class="min-w-0">
              <h3 :id="titleId" class="truncate text-lg font-extrabold text-neutral-950">{{ title }}</h3>
              <p v-if="description" :id="descriptionId" class="mt-0.5 text-xs text-neutral-500">{{ description }}</p>
            </div>
            <button class="app-button-soft shrink-0 rounded-lg border px-3 py-1.5 text-sm font-semibold transition-colors" type="button" @click="close">
              Cerrar
            </button>
          </div>
          <div class="max-h-[72vh] overflow-y-auto p-3.5 sm:p-4">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, required: true },
  description: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
const dialogRef = ref(null)
const triggerElement = ref(null)
const titleId = `modal-title-${Math.random().toString(36).slice(2)}`
const descriptionId = `modal-description-${Math.random().toString(36).slice(2)}`
const focusableSelector = [
  'button:not([disabled])',
  'a[href]',
  'input:not([disabled]):not([type="hidden"])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"]):not([disabled])',
].join(', ')

function getFocusableElements() {
  if (!dialogRef.value) return []

  return Array.from(dialogRef.value.querySelectorAll(focusableSelector)).filter((element) => {
    if (
      element.hidden ||
      element.matches(':disabled') ||
      element.getAttribute('aria-hidden') === 'true' ||
      element.closest('[hidden], [aria-hidden="true"]') ||
      element.getAttribute('tabindex') === '-1'
    ) {
      return false
    }

    const style = window.getComputedStyle(element)
    return style.display !== 'none' && style.visibility !== 'hidden' && element.tabIndex >= 0
  })
}

function focusFirstElement() {
  const [firstElement] = getFocusableElements()
  ;(firstElement || dialogRef.value)?.focus()
}

function handleKeydown(event) {
  if (event.key !== 'Tab' || !dialogRef.value) return

  const focusableElements = getFocusableElements()
  if (focusableElements.length === 0) {
    event.preventDefault()
    dialogRef.value.focus()
    return
  }

  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]
  const activeElement = document.activeElement

  if (!dialogRef.value.contains(activeElement)) {
    event.preventDefault()
    ;(event.shiftKey ? lastElement : firstElement).focus()
    return
  }

  if (event.shiftKey && activeElement === firstElement) {
    event.preventDefault()
    lastElement.focus()
  } else if (!event.shiftKey && activeElement === lastElement) {
    event.preventDefault()
    firstElement.focus()
  }
}

function handleFocusIn(event) {
  if (!dialogRef.value || dialogRef.value.contains(event.target)) return

  focusFirstElement()
}

function startFocusTrap() {
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('focusin', handleFocusIn)
}

function stopFocusTrap() {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('focusin', handleFocusIn)
}

function restoreTriggerFocus() {
  const element = triggerElement.value
  triggerElement.value = null

  if (!element || !element.isConnected || typeof element.focus !== 'function') return

  element.focus()
}

watch(
  () => props.modelValue,
  async (open) => {
    if (open) {
      triggerElement.value = document.activeElement
      await nextTick()
      if (!props.modelValue) return
      startFocusTrap()
      focusFirstElement()
      return
    }

    stopFocusTrap()
    await nextTick()
    restoreTriggerFocus()
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  stopFocusTrap()
  restoreTriggerFocus()
})

function close() {
  emit('update:modelValue', false)
}
</script>
