/**
 * Returns true when the element receiving focus on blur
 * is inside the given CSS selector.
 *
 * Replaces the `setTimeout(close, 200)` trick which fails on iOS
 * because `mousedown.prevent` does not delay the blur long enough.
 *
 * @param {FocusEvent} event The blur event from the input.
 * @param {string} selector CSS selector for the dropdown container.
 * @returns {boolean} true if the next focused element is inside the selector.
 */
export function focusInside(event, selector) {
  const next = event && event.relatedTarget
  if (!next || !selector) return false
  if (typeof next.closest !== 'function') return false
  return Boolean(next.closest(selector))
}
