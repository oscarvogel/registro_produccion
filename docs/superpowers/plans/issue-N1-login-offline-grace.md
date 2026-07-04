## Contexto

El operador trabaja en el campo y suele abrir la PWA sin cobertura. La app actualmente falla en ese escenario:

1. Al iniciar, `authStore.initAuth()` (en `frontend/src/stores/auth.js:82-87`) borra el token si está vencido.
2. El router guard (`frontend/src/router/index.js:90-104`) redirige a `/login`.
3. `/login` no puede hacer `POST /api/auth/login` porque no hay red.
4. Resultado: el operador queda atrapado en la pantalla de login sin poder trabajar.

## Comportamiento esperado

Si el operador ya inició sesión con éxito en los últimos N días en este dispositivo:

- Debe poder entrar a la app **sin tipear credenciales** aunque no haya red.
- La app debe mostrar un indicador claro "Modo offline – usando sesión guardada".
- Las acciones que requieren backend (cargar producción, sincronizar) deben seguir funcionando offline como ya lo hacen los catálogos.

## Solución propuesta

Cachear, luego de un login exitoso, un paquete con:

- `user`
- hash bcrypt-like de la contraseña (no la contraseña) o un refresh token de larga duración firmado por backend
- fecha del último login exitoso
- contador de días sin login válido contra servidor

En el arranque:

- Si hay red → intentar login silencioso con el refresh token o verificar el JWT actual; si vence, pedir credenciales.
- Si NO hay red → usar la sesión cacheada si está dentro del grace period (ej. 7 o 14 días desde el último login válido contra servidor).
- Si pasó el grace period → bloquear y pedir credenciales (seguridad: no dejar entrar eternamente offline).

## Tareas

1. Extender `frontend/src/stores/auth.js` con:
   - `cacheSession(user, passwordHash)` (se ejecuta al hacer login online con éxito).
   - `restoreCachedSession()` (se ejecuta al arrancar).
   - `extendOfflineGracePeriod` configurable desde `frontend/.env.example` (`VITE_OFFLINE_GRACE_DAYS`).
2. Modificar `initAuth()` para que distinga online/offline y aplique la política de gracia.
3. LoginView: si detecta sesión restaurada en offline, redirigir a home con toast "Modo offline activado".
4. Agregar test unitario cubriendo: online+token válido, online+token expirado, offline+cache fresco, offline+cache vencido.
5. Documentar la política en `README.md` y en comentarios del store.

## Criterios de aceptación

- En campo sin red, el operador con sesión reciente entra a la app sin tipear nada.
- Luego de N días sin un login online, la app obliga a tipear credenciales.
- No se guarda la contraseña en texto plano.
- El sync de registros pendientes sigue funcionando después del login offline.

## Prioridad

P0 — bloqueante para uso operativo en campo.

## Archivos clave

- `frontend/src/stores/auth.js`
- `frontend/src/views/LoginView.vue`
- `frontend/src/main.js`
- `frontend/.env.example` (nueva variable `VITE_OFFLINE_GRACE_DAYS`)
