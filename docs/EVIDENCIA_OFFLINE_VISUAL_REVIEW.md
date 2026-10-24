# Revisión visual — Modo offline de la evidencia (issue #202)

- **Fecha:** 2026-10-25
- **Rama:** `codex/issue-202-offline-evidencia`
- **Base:** `origin/main` (`63153c0`, PR #201 — captura en el formulario)
- **Alcance visual:** el circuito offline de la evidencia (banderita en *Pendientes*)
  y el comportamiento del formulario sin conexión.

## Comandos ejecutados

```bash
cd frontend
npm test                                   # 366 tests, 0 fallos
npm run check                              # lint + vue-tsc + build + PWA
node scripts/evidenciaOfflineSmoke.mjs     # smoke E2E + capturas reales (Playwright + Vite)
```

```bash
cd backend
venv\Scripts\python.exe -m pytest          # suite completa, 0 fallos
venv\Scripts\python.exe -m compileall -q app scripts
```

El smoke levanta Vite, mockea la API (catálogos, sesión y health check) y
**corta la red de verdad** (`context.setOffline(true)` + `navigator.onLine` en
`false`). En esa fase el mock aborta cualquier `POST` de producción: si el
formulario intentara subir algo sin conexión, el smoke falla en vez de dar un
falso verde.

## Flujo probado

1. Wizard de carga de producción hasta el paso **Evidencia** (7 de 10), con la
   foto de la pantalla del procesador cargada y la declaración de D7 tildada.
2. Se corta la conexión.
3. *Guardar Registro* → el registro **no se bloquea**: se avisa *"Guardado solo
   en este teléfono"* y la foto + el parte quedan en la base local del
   teléfono.
4. Pantalla **Registros Pendientes**: el operador ve el badge *"1 foto(s)
   adjunta(s), esperando subir"*.
5. Vuelve la conexión → el sync sube **primero la foto** y **después el
   parte**, y el parte lleva `evidencias: [id]`.
6. La pantalla de Pendientes se refresca sola: *"Todo sincronizado"*, cola
   vacía.

## Resultado de los tests

- `npm test`: **366 passed** (355 → 366; 11 nuevos).
  - `services/pendingEvidencias.test.js` (4): encolar, listar, marcar
    sincronizada y marcar con error.
  - `stores/produccionOfflineEvidencia.test.js` (4): el orden foto → parte, los
    ids en el payload, **no** enviar el parte si la foto no subió, y no tocar
    el payload cuando no hay foto.
  - `views/PendientesView.test.js` (+3): el badge de la foto, el aviso de "foto
    subida" y la recarga de la cola cuando el store sincroniza solo.
- `npm run check`: OK (build + PWA generada).
- Backend: suite completa OK (sin cambios de backend en este issue).
- `git diff --check`: limpio.

## Capturas

`docs/screenshots/evidencia_offline/` (ver el README de la carpeta).

| Archivo | Qué muestra |
|---|---|
| `01-evidencia-con-foto-1638x969.png` | Paso Evidencia con la foto y la declaración de D7. |
| `01b-paso-revision-1638x969.png` | Paso Revisión (10 de 10) con los pasos anteriores en `VALIDADO`. |
| `02-guardado-sin-conexion-1638x969.png` | Swal *"Guardado solo en este teléfono"* con la franja de "Sin conexión". |
| `03-pendientes-foto-en-espera-1638x969.png` | Badge *"1 foto(s) adjunta(s), esperando subir"* en la cola. |
| `04-pendientes-tras-sincronizar-1638x969.png` | Cola vacía y *"Todo sincronizado"* después del sync. |

## Hallazgos

1. **Sin conexión, el parte ya no se bloquea.** Antes de este issue el
   formulario avisaba *"Este tipo de proceso necesita la foto de evidencia y no
   hay conexión para subirla"* y **no guardaba nada**. Ahora el aviso es el
   inverso: *"Guardado solo en este teléfono"*, y tanto la foto como el parte
   quedan encolados.
2. **La foto y el parte comparten el `form_uuid`.** Sin eso el backend no
   puede vincular la evidencia con el registro al crearlo (R2). Verificado
   leyendo la base local del navegador: 1 fila en `pendingEvidencias` (blob de
   **90 616 bytes**, `synced = 0`) y 1 fila en `pendingRecords`, con el mismo
   `form_uuid`.
3. **El orden de subida es el correcto.** El smoke registra el orden real de
   las llamadas: `/api/produccion/evidencias` → `/api/produccion/`. Si la foto
   falla, el parte **no** sale (queda en la cola para el próximo intento) y el
   backend nunca recibe un parte sin la evidencia que su tipo de proceso exige
   (R2).
4. **Sin conexión no sale nada.** El mock aborta los `POST` de producción en
   esa fase y **no se registró ninguno**: el formulario ni intenta subir la
   foto ni el parte sin señal.
5. **El operador ve dónde está la foto.** El badge *"1 foto(s) adjunta(s),
   esperando subir"* en *Registros Pendientes* deja claro que la foto sigue en
   el teléfono. Después del sync, la cola queda vacía.
6. **La pantalla se refresca sola.** Este cambio salió del propio smoke: la
   app sincroniza por su cuenta (evento `online` o timer), sin pasar por el
   botón de la pantalla, y *Pendientes* seguía mostrando el parte como
   *"requieren atención"* con la foto *"esperando subir"*. Ahora un watcher
   sobre los contadores del store recarga la lista.

## Observaciones

- El toast *"Guardado solo en este teléfono"* (arriba a la derecha) tapa los
  botones *Refrescar* y *Sincronizar* durante los primeros segundos. Es el
  comportamiento global del componente de avisos, no algo de este issue, y el
  toast se cierra solo.
- En la captura `01` el rótulo del lateral dice *"Servidor disponible"*: el
  script mockea también el health check, como en las capturas del issue #200.
- Las capturas son a **1638x969** (la pantalla del cliente). Las pantallas con
  evidencia de los issues anteriores ya tienen su propia revisión visual
  (`docs/EVIDENCIA_FORM_VISUAL_REVIEW.md`).

## Veredicto

**aprobado visualmente.**

El operador no pierde la foto por estar sin señal, sabe que quedó en el
teléfono, y el servidor recibe primero la foto y después el parte.
