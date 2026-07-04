## Objetivo

Closes #51 (cierra también parcialmente el #24 — mensajes 5xx ya no leaken SQL/trazas)

Cuando el operador intenta login y algo falla, la pantalla de Login debe decirle **claramente qué pasó**:
- "Estás sin conexión" si está en el campo sin señal.
- "DNI o contraseña incorrectos" si escribió mal la credencial.
- "No se pudo conectar con el servidor" si el backend está caído (sin filtrar SQL ni stack traces).

## Cambios

- `frontend/src/stores/auth.js`
  - Nuevo helper `classifyLoginError(err)` que centraliza el mapeo axios error → mensaje amigable para el operador.
  - Constantes exportadas: `LOGIN_ERROR_NO_CONNECTION`, `LOGIN_ERROR_BAD_CREDENTIALS`, `LOGIN_ERROR_SERVER`.
  - `classifyLoginError()` rechaza eco de `data.detail` si es muy largo (>120 chars) o si luce técnico (regex sobre `pymysql`/`sqlalchemy`/`INSERT`/`SELECT`/`column`/`table`/`traceback`/`password_hash`/etc.).
  - `login()` ahora pasa `_suppressErrorToast: true` en el config para evitar el toast global duplicado.

- `frontend/src/services/api.js`
  - El interceptor de respuesta respeta el flag `_suppressErrorToast` (skipea todos los toasts).
  - Cubre 401 para requests no-login con un toast claro "Sesión expirada".
  - 5xx sigue usando `SERVER_ERROR_MESSAGE` (no leak), ahora también cuando es login (porque el flag lo silencia, pero por seguridad la rama 5xx del interceptor mantiene el genérico).

- `frontend/src/views/LoginView.vue`
  - Banner **amber persistente** "Estás sin conexión" arriba del formulario cuando `navigator.onLine === false`, escucha eventos online/offline.
  - Bloque de error con icono/color/título **diferenciado por categoría**:
    - `offline` → amber, icono offline, título "Sin conexión".
    - `credentials` → rojo, icono error, título "Credenciales incorrectas".
    - `server`/`other` → rojo, icono error, título "No se pudo validar el ingreso".
  - El subtítulo muestra `authStore.error` (texto amigable, sin SQL).

- Tests
  - `frontend/src/stores/auth.test.js` (+10) — clasificador, login payload, fallback técnico.
  - `frontend/src/services/api.test.js` reescrito (+6) — captura el handler del interceptor via mock de axios para testear 5xx, flag suppress, 401 cleanup, setUnauthorizedHandler.

## Tests / Validaciones

- [x] `git diff --check`
- [x] `npx vitest run` — **64/64 tests** (48 anteriores + 16 nuevos)
- [x] `npx vite build` — 9.59s, SW + manifest regenerados
- [x] sin nuevas warnings de CRLF en el diff

## Comportamiento por escenario

| Dispositivo | Status / error | Resultado visible |
|---|---|---|
| **Offline** | `err.response` undefined | Banner persistente + toast "Sin conexión" |
| Online, 401 | DNI mal | "Credenciales incorrectas" en rojo |
| Online, 5xx | Backend SQL leak | "No se pudo validar el ingreso" + sub "No se pudo conectar con el servidor…" (sin SQL) |
| Online, 400 corto | Backend dice "X inválido" | "No se pudo validar el ingreso" + sub "X inválido" (eco seguro) |
| Online, 400 técnico | Backend dice "INSERT INTO…" | Mensaje genérico, no se echo el SQL |
| Online, timeout | Sin response | "Sin conexión" (también mensaje amigable) |

## Fuera de alcance

- No se cambió el backend. El backend sigue mandando su `detail` técnico si quiere — el frontend ahora lo filtra para 5xx y para 4xx que luzca técnico.
- No se tocó el manejo 5xx fuera del flujo login (banner global). Eso entra en #34 si querés endurecer.

## Riesgos / pendientes

- El regex `looksTechnical` puede tener falsos positivos si el backend alguna vez manda un detail de 4xx que casualmente matchea (ej. "trace" en una palabra normal en español). Aceptable por ahora, se puede refinar en un follow-up.
- Si querés deshabilitar completamente la posibilidad de eco de 4xx detail, eso entra en hardening posterior. Hoy solo filtra técnicos.
