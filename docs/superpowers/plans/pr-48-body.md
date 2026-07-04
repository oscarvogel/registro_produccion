## Objetivo

Closes #48 (parte offline real del fix PWA)

Hoy un operador que abre la PWA sin señal queda atrapado en `/login` porque `initAuth()` borra el token vencido y no hay forma de revalidar contra el backend. Este PR agrega un **cache local seguro** de la sesión que se reusa automáticamente cuando el dispositivo está offline y dentro de un período de gracia configurable.

## Cambios

- `frontend/src/stores/auth.js`
  - Nuevo helper `hashSecret()` (SHA-256 vía WebCrypto, con fallback determinístico para tests).
  - Nuevos helpers `readOfflineSessionCache()`, `readOfflineGracePeriodDays()`, `clearOfflineSessionCache()`.
  - Nuevas acciones `cacheSession(password)` (se ejecuta tras un login online exitoso), `restoreCachedSession()`, `clearOfflineCache()`.
  - `login()` ahora cachea la sesión al autenticarse online.
  - `logout()` mantiene el cache (el operador puede volver dentro del período de gracia).
  - `initAuth()` devuelve uno de cuatro modos: `online`, `offline`, `offline-locked`, `login-required`.
  - Nuevo getter `isAuthenticatedOffline` para que el router-guard acepte sesiones cacheadas.
  - Nuevo state `offlineMode` y `initMode` para que la UI sepa en qué modo arrancó.

- `frontend/src/router/index.js`
  - El guard global ahora considera `isAuthenticated || isAuthenticatedOffline` para decidir si pide login.

- `frontend/src/main.js`
  - Después de `initAuth()`, si el modo fue `offline`, dispara un toast diferido (`Modo offline`) para que el operador sepa que entró con sesión cacheada.

- `frontend/src/views/LoginView.vue`
  - Al montar, si la sesión offline restaurada es válida, redirige a home.
  - Si está offline y el cache pasó la gracia, muestra aviso amber explicando por qué no puede entrar.
  - Tras login online exitoso, limpia el cache (ya quedó reemplazado por uno fresco).
  - Soporta `?redirect=…` cuando se llega al login con sesión aún válida.
  - Mensaje de error diferenciado para login offline: "Estás sin conexión. Necesitamos señal para validar el ingreso."

- `frontend/.env.example`
  - Nueva variable `VITE_OFFLINE_GRACE_DAYS=14` (rango válido 1..365).

- `frontend/src/stores/auth.test.js` (nuevo)
  - 12 tests cubriendo: JWT válido, JWT expirado online, offline+cache fresco, offline+cache fuera de gracia, helpers de cache, login online cachea, logout preserva cache, `clearOfflineCache` borra, mensajes de error de login (401 vs 5xx sin leak).

- `docs/superpowers/plans/issue-N1..N4.md`
  - Borradores locales de las 4 issues abiertas (#48..#51) para referencia.

## Tests / Validaciones

- [x] `git diff --check` (sin warnings de whitespace)
- [x] `npx vitest run` — **48/48 tests pasaron** (36 originales + 12 nuevos)
- [x] `npx vite build` — terminó OK en 8.29s, SW + manifest regenerados
- [x] `npm install` — sin vulnerabilidades nuevas

## Comportamiento por escenario

| Estado del dispositivo | Token vigente | Cache fresca | Resultado |
|---|---|---|---|
| Online | Sí | * | online — entra con JWT |
| Online | No | * | login-required — va a `/login` |
| Offline | * | Sí (dentro de gracia) | offline — entra sin tipear nada |
| Offline | * | No existe / vencida | offline-locked — ve aviso amber explicando |

## Fuera de alcance

- Backend no se tocó: la solución es 100% frontend (WebCrypto + localStorage).
- No se implementó todavía: banner persistente en todas las vistas (#50), healthcheck `/api/health` (#49), clasificación detallada de errores 5xx (#51). Esos quedan para los próximos PRs.

## Riesgos / pendientes

- SHA-256 de la contraseña es **defensa complementaria**, no seguridad real: si el atacante accede al localStorage puede ver el hash. La gracia offline es una conveniencia operacional; el backend sigue siendo la autoridad. La gracia por defecto es 14 días, configurable.
- Si el operador cambia la contraseña desde otro dispositivo, este cache local seguirá aceptando la contraseña vieja hasta que pase la gracia. Si querés invalidación inmediata, eso requiere backend (refresh token firmado) — agendado como follow-up.
- No toqué backend en este PR. PR siguiente (issue #51) puede tocar el interceptor de errores de `/api/auth/login` para no leakear detalles.
