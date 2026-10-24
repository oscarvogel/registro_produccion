# Revisión visual — Admin de Tipos de Proceso con evidencia (issue #194)

## Fecha

2026-10-24

## Rama / commit validado

- Rama: `codex/issue-194-esquema-evidencia`
- Commit: `9205634` + los cambios de evidencia visual de este PR
- Base: `origin/main` @ `b0be309`

## Qué se cambió

Los flags de exigencia de evidencia fotográfica (`requiere_foto_horometro` y
`requiere_foto_procesador`) se administran desde el Admin de Tipos de Proceso:

- dos checkboxes nuevos en la pestaña **Requisitos** del formulario;
- una columna **Evidencia** en la grilla que resume qué exige cada proceso.

## Comandos ejecutados

```bash
cd frontend
node scripts/evidenciaAdminCapture.mjs        # capturas + medicion de desborde
npx vitest run src/views/admin/AdminCrudView.test.js
npm test                                       # suite completa
npm run check                                  # build vite + PWA
```

## Resultado de tests

| Comando | Resultado |
|---|---|
| `npx vitest run src/views/admin/AdminCrudView.test.js` | 13 passed |
| `npm test` | 53 archivos / 335 tests passed |
| `npm run check` | OK (PWA generada) |
| `python -m pytest` | 313 passed |
| `python -m compileall app` | exit 0 |

## Flujo probado

1. Entrar a **Administración → Tipos de Proceso**.
2. Ver la grilla: la columna **Evidencia** muestra `Ambas`, `Procesador`,
   `Horómetro` o `—` según lo que exige cada tipo de proceso.
3. Click en **Nuevo** → pestaña **Requisitos**: aparecen los checkboxes
   *Requiere Foto Horómetro* y *Requiere Foto Procesador*, con el texto de ayuda
   que explica que son la evidencia fotográfica.

## Screenshots

Carpeta: `docs/screenshots/evidencia_admin/`

| Captura | Resolución | Qué muestra |
|---|---|---|
| `01-admin-tipos-lista-1638x969.png` | 1638x969 | grilla con la columna Evidencia (pantalla del cliente) |
| `01-admin-tipos-lista-1366x768.png` | 1366x768 | grilla con scroll horizontal de 37px |
| `01-admin-tipos-lista-390x844.png` | 390x844 | vista de tarjetas en celular |
| `02-admin-requisitos-evidencia-1638x969.png` | 1638x969 | formulario, pestaña Requisitos |
| `02-admin-requisitos-evidencia-1366x768.png` | 1366x768 | formulario, pestaña Requisitos |
| `02-admin-requisitos-evidencia-390x844.png` | 390x844 | formulario en celular |

## Hallazgos

### H-1 — La grilla no tenía margen: dos columnas rompían la pantalla

La primera implementación agregó **dos** columnas a la grilla (*Foto Horómetro* y
*Foto Procesador*). Medido con el script de captura:

| Estado | 1366x768: desborde |
|---|---|
| Antes del cambio | **0 px** |
| Con dos columnas | **208 px** |
| Con una columna combinada | **37 px** |

Con dos columnas, la columna **Acciones** (Editar / Desactivar) quedaba
*completamente* fuera de pantalla y había que hacer scroll horizontal para
llegar a los botones.

**Resolución:** se implementó **una sola columna "Evidencia"** que resume los dos
flags (`Ambas` / `Horómetro` / `Procesador` / `—`). Además de recuperar 171px de
ancho, la columna se lee mejor: responde de una "¿qué evidencia exige este
proceso?" en vez de obligar a cruzar dos Sí/No.

El resumen se calcula con un hook `decorate` por entidad en `AdminCrudView.vue`,
sin tocar el contrato del componente `DataTable`.

### H-2 — Quedan 37px de scroll horizontal a 1366x768

Con la columna combinada, la grilla necesita 1067px y hay 1030px visibles.
Es un scroll chico: la grilla ya tiene `overflow-x-auto` y es el comportamiento
esperado de `DataTable` cuando la tabla no entra.

En **1638x969** (la pantalla del cliente) el desborde es **0px**: todo se ve
completo, incluidas las acciones de la fila.

Observación: la grilla de tipos de proceso entra **exacta** en 1366px, sin
margen. Cualquier columna nueva la desborda. Si se agrega otra columna en el
futuro, conviene revisar el ancho de las acciones o acortar los botones.

### H-3 — El texto de ayuda del formulario se volvió largo

Se reescribió el `formHint` para explicar los dos flags nuevos. Se verificó que
no rompe el layout del formulario a las tres resoluciones.

### H-4 — La medición se hace con datos reales

La primera medición usaba un nombre de unidad de negocio largo
("UNIDAD NEGOCIO DEMO FORESTAL") que no es el de producción. En la base real los
tipos de proceso de producción están vinculados a la UN 144 **"Caminos"**
(`unidadnegocio_tipo_proceso`). El mock de la captura usa esos datos reales, y
el script imprime el ancho de cada columna para poder comparar.

## Veredicto

**aprobado con observaciones**

- El formulario (checkboxes) queda perfecto en las tres resoluciones.
- La grilla entra completa en la resolución del cliente (1638x969) y en celular.
- A 1366x768 queda un scroll horizontal de 37px, aceptable y menor que el que
  había antes de este cambio (208px con dos columnas).
- Queda pendiente de decisión del usuario si se prefiere **sacar** la columna
  "Evidencia" de la grilla para llegar a 0px de desborde a 1366x768, dejando la
  configuración sólo en el formulario.
