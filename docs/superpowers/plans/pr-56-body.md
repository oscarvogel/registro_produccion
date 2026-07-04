## Objetivo

Closes #56

Dos problemas del operador en campo sin red:

1. **Confusion UX**: el banner amber dice "sin conexion" pero la app igual le pide login, sin explicar que tiene que tipear DNI+contraseña **una vez con internet** para guardar la sesion offline.
2. **Ruido**: cada request que falla por falta de red dispara un toast "Backend no disponible" que se suma al banner ya presente. Doble senial, mismo mensaje, mal experiencia.

## Cambios

- **`frontend/src/components/ui/OfflineBanner.vue`** — nuevo prop `hasCachedSession` (default `true`). Cuando es `false` (operador nunca se logueo en este dispositivo), el banner muestra el texto "primera vez: necesitas iniciar sesion una vez con internet para guardar tu sesion hasta 14 dias". Cuando es `true`, mantiene el copy vigente ("se guardan localmente y se sincronizan al reconectar").
- **`frontend/src/App.vue`** — pasa `:has-cached-session="!!authStore.cachedSession"` al banner.
- **`frontend/src/views/LoginView.vue`** — cuando estamos offline y NO hay `cachedSession`, muestra dentro del form un aviso contextual explicando el requisito de la primera vez con internet.
- **`frontend/src/services/api.js`** — el interceptor global suprime el toast "Backend no disponible" cuando la falla es por falta de respuesta (`!error.response`) Y el operador esta offline (`connectivityStore.isOffline === true`). El banner amber ya cubre esa senial. Los 5xx y 401 no-login siguen mostrandose porque requieren accion explicita del operador.
- **Tests**: +7 cases en `OfflineBanner.test.js` cubriendo las 4 ramas del copy y la prop de pendingCount. +4 cases en `api.test.js` cubriendo silencio offline, 5xx sigue activo, 401 sigue activo.

## Tests / Validaciones

- [x] `git diff --check` (limpio)
- [x] `npx vitest run` — **81/81 tests** (77 anteriores + 11 nuevos)
- [x] `npx vite build` — OK, SW + manifest regenerados
- [x] Manual: banner aparece con copy distinto segun historial del dispositivo

## Comportamiento esperado

| Escenario | Banner arriba | Toast "Backend no disponible" |
|---|---|---|
| Online + red OK | (no aparece) | - |
| Online + pero backend 5xx | (no aparece) | aparece ("Error del servidor") |
| **Offline + ya logueado antes** | amber, copy "se guardan localmente" | **silenciado** (banner ya avisa) |
| **Offline + primera vez (sin cache)** | amber, copy "primera vez: necesitas validar DNI una vez con internet" | **silenciado** |
| Operador hace login mientras offline | - | aparecia en "sesion expirada" si 401, pero login ahora usa `_suppressErrorToast` |

## Fuera de alcance

- Healthcheck real (`/api/health`) para distinguir "sin internet" vs "backend caido con red" — sigue pendiente para #49.
- Migrar el codigo del interceptor para que use `isBackendUp` directo (no requiere healthcheck todavia).

## Riesgos / pendientes

- Si el operador esta online con Wi-Fi y el backend esta saludable, el toast 5xx NO deberia aparecer — efectivamente, no aparece (es solo para errores 5xx).
- Si `useConnectivityStore()` falla (por ej. cuando se importa el modulo en tests con auto-mock que no setea getters), retorna `false` para `isOffline` (gracias al try/catch con fallback). El comportamiento por default es mostrar el toast (no silenciar), que es lo seguro.
