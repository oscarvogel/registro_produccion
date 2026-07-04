## Objetivo

Closes #50

Hoy el banner offline solo aparecía cuando el operador ya estaba autenticado (`App.vue` lo tenía dentro del `v-if="authStore.isAuthenticated"`). Un operador que abre la app sin red y sin sesión cacheada válida quedaba sin feedback hasta escribir credenciales — y eso se siente como "la app se colgó". Este PR mueve el banner a una capa global y centraliza la detección online/offline en un store reusable.

## Cambios

- `frontend/src/stores/connectivity.js` (nuevo): store Pinia que envuelve `navigator.onLine` + listeners `online`/`offline`. Expone `isOnline`, `isOffline`, `isBackendUp`, `lastBackendCheckAt`. `init()` se llama una sola vez desde `main.js` y es idempotente.
- `frontend/src/components/ui/OfflineBanner.vue` (nuevo): componente reutilizable que muestra el banner amber. Vive **fuera** del `v-if` del auth store, así que aparece también en `/login`.
- `frontend/src/App.vue`: el banner ahora es `<OfflineBanner :pending-count="produccionStore.pendingCount" />`. Indicadores "En línea / Sin conexión" del sidebar y header leen del store. Eliminé listeners duplicados.
- `frontend/src/main.js`: llama `connectivityStore.init()` después de `createApp`.
- `frontend/src/views/LoginView.vue`: removido `offlineNow` local, listeners y los dos bloques de banner (desktop + mobile). Ahora se riega desde el store.
- `frontend/src/stores/connectivity.test.js` (nuevo): 6 tests — init, cambio por evento offline, online optimista, idempotencia, SSR-safe.

## Tests / Validaciones

- [x] `git diff --check` (solo warnings LF/CRLF normales en Windows, no errores)
- [x] `npx vitest run` → **70/70 tests** (64 anteriores + 6 nuevos, sin regresión)
- [x] `npx vite build` → 8.38s, SW + manifest regenerados

## Comportamiento por escenario

| Estado | Banner top | Login offline notice | Sidebar indicator |
|---|---|---|---|
| Online + autenticado | (no banner) | (no aplica) | "En línea" |
| Offline + autenticado | amber con pendientes (si hay) | (no aplica) | "Sin conexión" |
| Online + no autenticado | (no banner) | (no aplica) | (no aplica, está en /login) |
| **Offline + no autenticado + cache fresca** | **amber** | "Tu sesión guardada..." → home | "Sin conexión" |
| Offline + no autenticado + cache vencida | amber | "tu sesión guardada tiene X días..." | (no aplica) |

## Fuera de alcance

- No se implementó el healthcheck real (`/api/health`). El store ya tiene `isBackendUp` listo para eso (issue #49), pero por ahora se inicializa siguiendo `isOnline`.
- No agregué un test del banner en sí mismo (jsdom + Vue Testing Utils sería scope creep para este PR chico).

## Riesgos / pendientes

- El componente `OfflineBanner` solo se monta una vez por sesión (en `App.vue`). Esto es intencional — si en el futuro hace falta banners adicionales por vista (ej. dentro de `ProduccionFormView` para avisos de catálogo desactualizado), conviene refactorear a un sistema de toasts más rico.
- Cuando llegue #49, `isBackendUp` pasará a depender de un ping real a `/api/health`. La UI ya está preparada (el banner cambia a rojo si `!isBackendUp` y `isOnline`).
