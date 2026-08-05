# Issue #123 — Modal "Detalle del registro" se abre vacío

## Contexto

En la pantalla `/dashboard/registros` (y también en `OperadorView`) el botón **"Ver detalle"** sobre una fila de operación abre el modal `RecordDetailModal`, pero el cuerpo queda en blanco: solo se ve el título "Detalle del registro" y el botón "Cerrar". No hay spinner de carga, no hay error, no hay datos.

URL reportada: `https://produccion.servinlgsm.com.ar/dashboard/registros?un_id=106&fecha_desde=2026-08-04&fecha_hasta=2026-08-04`

Captura: ver `docs/screenshots/issue-123-modal-vacio/` (a guardar al implementar).

## Comportamiento esperado

Al hacer click en **"Ver detalle"** sobre cualquier registro, el modal debe:

1. Mostrar un spinner breve mientras carga.
2. Renderizar el resumen completo del registro agrupado por secciones (Identificación, Horario, Producción, Consumos, Ubicación, Remitos, Observaciones) tal como ya está definido en el array `grupos` del componente.
3. Mostrar el id del registro en el footer y los chips de título/descripción (`<operación> - <fecha>` / `<operador> - <equipo>`).

## Comportamiento actual

- Modal abre.
- Spinner **no** aparece (no se dispara el fetch).
- Bloque de error no aparece.
- Bloque con datos no aparece.
- Solo queda el header con título y el botón Cerrar.

## Causa raíz (identificada en código)

En `frontend/src/components/registros/RecordDetailModal.vue`, el `watch` que debería disparar la carga está condicionado al flag `useStore`:

```js
// RecordDetailModal.vue
watch(
  () => [props.modelValue, props.registroId],
  async ([open, id]) => {
    if (open && id && !props.useStore) {   // <-- solo dispara si useStore === false
      await store.fetchDetalle(id)
    } else if (!open) {
      store.clearDetalle()
    }
  },
  { immediate: true },
)
```

Con la prop por default:

```js
const props = defineProps({
  ...
  useStore: { type: Boolean, default: true },   // <-- default true
})
```

Ambos call-sites pasan el modal **sin** `:use-store="false"`:

- `frontend/src/views/DashboardRegistrosView.vue:215-218`
  ```vue
  <RecordDetailModal
    v-model="detalleOpen"
    :registro-id="detalleId"
  />
  ```
- `frontend/src/views/OperadorView.vue:142`
  ```vue
  <RecordDetailModal v-model="detalleOpen" :registro-id="detalleId" />
  ```

Resultado: cuando el usuario hace click en "Ver detalle", el watcher evalúa `open && id && !props.useStore` → `true && true && !true` → `false`. Nunca se llama a `store.fetchDetalle(id)`. `store.detalle` queda en `null`, `detalleLoading` en `false`, `detalleError` en `null`, y el template no entra en ninguna rama de los `v-if`, dejando el cuerpo vacío.

`store.fetchDetalle` (en `frontend/src/stores/dashboardRegistros.js:113`) es el único path que puebla `state.detalle`, y ningún consumidor lo llama antes de abrir el modal → el modal nunca puede mostrar datos con la configuración actual.

## Tareas

1. **Decidir el contrato del modal.** Hay dos opciones razonables:
   - **A. Siempre fetchear al abrir** (recomendado): eliminar la prop `useStore` y llamar siempre a `store.fetchDetalle(id)` cuando `open && id`. Es la opción más simple y coherente con la intención de un modal de "ver detalle" (siempre trae el detalle fresco del backend).
   - **B. Cambiar el default a `false`**: pasar `:use-store="false"` en los call-sites (o cambiar el `default` de la prop a `false`). Funciona pero deja la prop sin uso real y obliga a todos los call-sites a acordarse de pasarla.

   Recomiendo A: borrar la prop `useStore`, simplificar el watcher a `if (open && id) await store.fetchDetalle(id)`, y eliminar cualquier llamada previa a `fetchDetalle` que estuviera haciendo de workaround (verificar que no exista).

2. **Limpiar `clearDetalle` al cerrar.** Mantener el `else if (!open) { store.clearDetalle() }` para que la próxima apertura haga fetch fresco y no muestre datos stale.

3. **Manejar el caso de error 404 / 5xx con UI clara** (ya hay rama `v-else-if="error"` que muestra mensaje). Verificar que `_suppressErrorToast: true` en `api.get` no tape el mensaje de error que el modal ya muestra.

4. **Tests** (en `frontend/src/stores/dashboardRegistros.test.js` y, si existe, test del modal):
   - Al abrir el modal con un `registroId` válido se llama a `fetchDetalle` una vez.
   - Al cerrar el modal se llama a `clearDetalle` (o el estado `detalle` queda en `null`).
   - Al reabrir con otro id se vuelve a fetchear.
   - Si el backend responde 404, el modal muestra el mensaje de error (no rompe).

5. **Validación visual con Computer Use** en `produccion.servinlgsm.com.ar`:
   - Capturar `docs/screenshots/issue-123-modal-vacio/01-antes.png` (modal vacío actual) — opcional, sirve de baseline.
   - Capturar `docs/screenshots/issue-123-modal-vacio/02-despues-loading.png` (spinner).
   - Capturar `docs/screenshots/issue-123-modal-vacio/03-despues-datos.png` (modal con datos completos).
   - Capturar `docs/screenshots/issue-123-modal-vacio/04-despues-error.png` (modal con error 404 forzado).

## Criterios de aceptación

- [ ] Click en "Ver detalle" sobre cualquier registro abre el modal y muestra el resumen completo del registro.
- [ ] Modal muestra spinner breve mientras carga.
- [ ] Modal muestra mensaje de error legible si el backend responde 404 o 5xx (sin stack técnico).
- [ ] Al cerrar y volver a abrir, los datos se vuelven a fetchear (no quedan stale).
- [ ] Funciona igual en `/dashboard/registros` y en la vista de Operador.
- [ ] `git diff --check` limpio.
- [ ] Suite de tests de frontend en verde (`npx vitest run` o el comando del proyecto).
- [ ] Evidencia visual guardada en `docs/screenshots/issue-123-modal-vacio/`.

## Prioridad

P1 — bug visible en producción que rompe una funcionalidad principal del dashboard.

## Archivos clave

- `frontend/src/components/registros/RecordDetailModal.vue` (fix principal)
- `frontend/src/stores/dashboardRegistros.js` (revisar que `fetchDetalle` se siga llamando)
- `frontend/src/views/DashboardRegistrosView.vue` (call-site, sin cambios esperados si la solución es A)
- `frontend/src/views/OperadorView.vue` (call-site, sin cambios esperados si la solución es A)
- `frontend/src/stores/dashboardRegistros.test.js` (tests)
