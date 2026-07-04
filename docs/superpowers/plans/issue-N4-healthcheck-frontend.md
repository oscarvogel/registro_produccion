## Contexto

El backend ya tiene `/api/health` (en `backend/app/main.py:88-127`, resuelve issue #33 que aún está abierto). El frontend, sin embargo, no lo usa. Esto significa que cuando un operador tiene señal Wi-Fi o 4G pero el backend está caído, ve el mismo error que si estuviera sin cobertura.

## Comportamiento esperado

- Al iniciar la app, si `navigator.onLine === true`, intentar un `GET /api/health` (con timeout corto, ej. 3s).
- Si responde 200 → backend OK.
- Si responde 503 → mostrar "Servidor en mantenimiento, reintentando…".
- Si no responde (timeout / error de red) → usar estado "sin red" (entrar en modo offline con sesión cacheada).

## Tareas

1. Crear `frontend/src/services/healthCheck.js` con `checkBackend()` que hace GET a `/api/health` con timeout 3s.
2. Llamarlo en `main.js` antes del router-guard y guardar el resultado en un store nuevo (`frontend/src/stores/connectivity.js`) con flags `isOnline` y `isBackendUp`.
3. Reemplazar el `isOnline` de `App.vue` por el nuevo store.
4. Mostrar mensajes diferentes en LoginView según `isOnline` vs `isBackendUp`.
5. Test unitario cubriendo: timeout, 200, 503, error de red.

## Criterios de aceptación

- El frontend puede distinguir "sin internet" de "backend caído" en menos de 3s.
- El banner amarillo cambia su mensaje según `isBackendUp`.
- Cachear el último estado `isBackendUp` en localStorage con TTL de 30s para no martillar el endpoint.

## Prioridad

P1 — mejora significativa de DX.
