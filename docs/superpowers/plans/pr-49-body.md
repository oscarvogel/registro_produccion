## Objetivo

Closes #49

Hasta ahora el operador no podia distinguir "estoy sin internet" de "el backend esta caido" (red OK pero servicio muerto). Hoy cualquier falla de request mostraba el mismo toast "Backend no disponible". Esto bloquea el caso operacional donde, por ejemplo, alguien toca el cortafuegos del backend y el operador entra en panico.

## Cambios

- **`frontend/src/services/healthCheck.js`** (nuevo) — `checkBackend()` hace `GET /api/health` con `AbortController` (3s timeout). Bypassea axios y los interceptores globales para no contaminar con toasts o handlers 401. Devuelve `'ok' | 'degraded' | 'unreachable' | 'timeout'`. Normaliza `baseURL` igual que el cliente axios (colapsa `/api` y `/api/` a vacio).

- **`frontend/src/stores/connectivity.js`**
  - Estado: `isBackendUp`, `lastBackendCheckAt`, `lastHealthResult`, `pendingInitialHealthCheck`.
  - Acciones nuevas: `refreshBackendHealth({ force })`, `startPeriodicHealthChecks()`, `stopPeriodicHealthChecks()`, `teardown()`.
  - `init()` ahora usa handlers nombrados para poder remover listeners (necesario para tests).
  - Al volver online dispara healthcheck inmediato.
  - Getters: `isBackendDegraded`, `isOfflineOrBackendDown`, `hasFreshBackendState` (TTL 30s).

- **`frontend/src/main.js`** — tras `init()` corre `refreshBackendHealth()` no bloqueante + `startPeriodicHealthChecks()` cada 30s.

- **`frontend/src/components/ui/OfflineBanner.vue`** — usa `isOfflineOrBackendDown` para decidir visibilidad. Fondo **rojo** cuando online pero backend degradado; amber cuando offline.

- **`frontend/src/services/api.js`** — el interceptor suprime el toast "Backend no disponible" cuando `isOfflineOrBackendDown === true` (el banner ya avisa). 401 y 5xx siguen mostrandose porque requieren accion.

- **Tests**:
  - +10 cases en `healthCheck.test.js` (cubren ok/degraded/unreachable/timeout + URLs normalizados).
  - +10 cases en `connectivity.test.js` (refreshBackendHealth, cache TTL, periodic, teardown).
  - +1 ajuste mock en `api.test.js` para reflejar el nuevo getter.

## Tests / Validaciones

- [x] `git diff --check` (limpio)
- [x] `npx vitest run` — **95/95** tests (anterior 81 + 14 nuevos)
- [x] `npx vite build` — OK, SW + manifest regenerados

## Comportamiento esperado

| Estado | `isOnline` | `isBackendUp` | Banner | Toast `Backend no disponible` |
|---|---|---|---|---|
| Todo OK | true | true | (no) | (no) |
| Sin internet | false | false | amber | (silenciado) |
| **Red OK pero backend 5xx** | true | false | **rojo** | (silenciado) |
| Backend 503 degradado | true | false | rojo | (silenciado) |

## Fuera de alcance

- Ajustes al backend healthcheck (`/api/health` ya existe en `backend/app/main.py`, valida DB).
- Cache permanente del estado de healthcheck en localStorage — vive solo en memoria del store.
- Reintento automatico cuando el healthcheck falla.

## Riesgos / pendientes

- El healthcheck dispara cada 30s. Bajo Wi-Fi fragil o backend lento, los timeouts pueden sumar ruido. Si molesta, se sube el intervalo via `startPeriodicHealthChecks({ intervalMs: 60_000 })`.
- Si vite-plugin-pwa cachea agresivamente, podria servir un SW viejo. Limpiar cache del navegador en la primera prueba.
