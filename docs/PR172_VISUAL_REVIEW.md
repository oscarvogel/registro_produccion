# PR #172 — Revisión visual del circuito offline PWA

## Datos

- **Fecha**: 2026-10-23
- **Rama**: `fix/pwa-offline-reconcile-165` (PR #172), rebasada sobre `origin/main`
- **Commit validado**: `60829c5` (más el fix de legibilidad que se suma en este PR)
- **Ambiente**: Windows 11, Node 20, Playwright + Chromium, Vite dev server con la API interceptada por mock (sin MySQL ni backend de producción)

## Comandos ejecutados

```bash
cd frontend
npm test                    # 333 passed (53 archivos)
npm run check               # build + service worker: OK
node scripts/pwaOfflineSmoke.mjs   # smoke del circuito offline: OK
```

Backend (sin cambios en este PR):

```bash
cd backend
python -m pytest -q         # OK (exit 0)
```

## Flujo probado

1. **Login online** → la app entra al inicio y deja la sesión offline cacheada (`offline_session_cache` en `localStorage`).
2. **Reapertura sin token y sin red** → la app entra con la sesión cacheada: layout completo, navegación, KPIs, "Ver Pendientes" y banner "Sin conexión — los registros se guardan localmente y se sincronizan al reconectar".
3. **Vuelve la conexión** → la app redirige a `/login?redirect=/&reauth=1` con el aviso "Volvió el servidor. Validá tu DNI y contraseña para enviar automáticamente los registros pendientes." (la cola de pendientes se conserva).

## Screenshots

- `docs/screenshots/pr-172-pwa-offline/01-inicio-online.png`
- `docs/screenshots/pr-172-pwa-offline/02-sesion-offline.png`
- `docs/screenshots/pr-172-pwa-offline/03-reautenticacion.jpg`

(Ver `docs/screenshots/pr-172-pwa-offline/README.md`.)

## Hallazgos

### 1. Aviso de reautenticación ilegible en tema oscuro — **corregido en este PR**

El aviso de la pantalla de login usa `bg-amber-100 text-amber-900`. En tema oscuro el proyecto fuerza `text-amber-900` a `var(--color-idle-text)` (`#fac775`), pero **no** tenía override para `bg-amber-100`: el fondo quedaba en ámbar claro sólido y el texto en el mismo ámbar → **texto invisible sobre fondo idéntico**.

Se agrega el override faltante en `frontend/src/style.css`:

```css
:root[data-theme="dark"] .bg-amber-100 {
  background-color: var(--color-idle-bg) !important;
}
```

Verificado con `getComputedStyle`: fondo `rgba(250, 199, 117, 0.12)`, texto `rgb(250, 199, 117)`.

El bug es preexistente en `main` (afectaba a todos los avisos offline de la pantalla de login), pero este PR los vuelve visibles en el flujo de reautenticación, así que se corrige acá.

### 2. `docs:capture` roto en `main` — **fuera de alcance, queda reportado**

`npm run docs:capture` falla en `main`: el script busca un botón "Sincronizar" y los `aria-label` "Abrir navegacion"/"Cerrar menu" (sin acentos) que ya no existen después del rediseño de la navegación móvil. Además el script intercepta `**/api/**` y el probe de salud ahora pega a `/health`, que quedaba sin mock.

En este PR **sólo** se mockea `/health` en `docsCapture.mjs` (necesario por el cambio de probe). Los selectores obsoletos se dejan como estaban y se reporta como issue aparte: regenerar las capturas del manual y el PDF es otro trabajo.

### 3. Riesgo de negocio R4 — **abierto, no es visual**

La cache de sesión offline sobrevive si el operador B entra online en el mismo dispositivo sin que el operador A haya hecho logout. `requireOnlineReauth()` mitiga el envío con un token ajeno (punto 3 del flujo), pero la limpieza de cache al login de otro operador requiere una regla de negocio.

## Límites de la evidencia

El smoke intercepta la API con un mock: **no** verifica la persistencia real en MySQL ni la deduplicación por `form_uuid`. Eso sigue pendiente en el issue #164, que queda abierto.

## Veredicto

**Aprobado visualmente** (con las observaciones 1 y 2 registradas: la 1 corregida en este PR, la 2 derivada a issue aparte).
