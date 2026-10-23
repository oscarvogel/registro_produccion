# Evidencia visual — PR #172 (circuito offline PWA)

Capturas del smoke del circuito offline ejecutadas sobre la rama
`fix/pwa-offline-reconcile-165` (PR #172), con la app servida por Vite y la API
interceptada por un mock (sin MySQL ni backend de producción).

- **Script**: `frontend/scripts/pwaOfflineSmoke.mjs`
- **Comando**: `cd frontend && node scripts/pwaOfflineSmoke.mjs`
- **Viewport**: 1638x969 (resolución de la compu del cliente)

## Capturas

| Archivo | Qué muestra |
| --- | --- |
| `01-inicio-online.png` | Login online correcto: la app entra al inicio y **deja la sesión offline cacheada** (`offline_session_cache` presente en `localStorage`). |
| `02-sesion-offline.png` | App reabierta **sin token y sin red**: entra con la sesión cacheada, muestra el **layout completo** (sidebar, navegación, KPIs, "Ver Pendientes") y el banner "Sin conexión — los registros se guardan localmente y se sincronizan al reconectar". |
| `03-reautenticacion.jpg` | Al **volver la conexión**, la app redirige a `/login?redirect=/&reauth=1` con el aviso "Volvió el servidor. Validá tu DNI y contraseña para enviar automáticamente los registros pendientes." |

## Resultado del smoke

```
1. login online -> / | cache offline: true | token: true
2. arranque sin red -> / | layout: true | cache: true | token: false | banner: Sin conexión - los registros se guardan localmente y se sincronizan al reconectar
3. vuelve la conexion -> /login?redirect=/&reauth=1 | aviso visible: true | Volvió el servidor. Validá tu DNI y contraseña para enviar automáticamente los registros pendientes.
```

El script falla con código de salida 1 si algún punto no se cumple (cache
ausente, layout incompleto, token conservado en modo offline, reautenticación
no pedida o aviso ilegible).

## Límites de esta evidencia

El smoke usa la API mockeada: **no** verifica la persistencia real en MySQL ni
la deduplicación por `form_uuid`. Eso sigue pendiente en el issue #164, que
por eso sigue abierto.
