# Revisión visual — Verificación de la evidencia por el encargado (issue #204)

- **Fecha:** 2026-10-25
- **Rama:** `codex/issue-204-verificacion-evidencia`
- **Base:** `origin/main` (`31c8439`, PR #203 — modo offline de la evidencia)
- **Alcance visual:** la sección de evidencia del detalle del registro, los
  botones Verificar / Rechazar, el filtro de evidencia del listado y las
  marcas de registro observado.

## Comandos ejecutados

```bash
cd frontend
npm test                                   # 388 tests, 0 fallos
npm run check                              # lint + vue-tsc + build + PWA
node scripts/evidenciaVerificacionCapture.mjs   # capturas reales + verificación
```

```bash
cd backend
venv\Scripts\python.exe -m pytest
venv\Scripts\python.exe -m compileall -q app scripts
```

La captura levanta Vite con la API mockeada (listado, detalle, lista de
evidencias, descarga del archivo y el `PATCH` de verificación). El script
**falla** si la sección no aparece, si el encargado no ve los botones, si el
filtro no filtra o si algo se sale de la pantalla.

## Flujo probado

1. El encargado entra a *Detalle de registros* con la unidad ya filtrada.
2. El listado muestra el filtro de evidencia y marca cada registro según el
   estado de sus fotos.
3. Con el filtro *Esperando verificación* quedan solo los registros con fotos
   sin revisar.
4. Al abrir el detalle aparece la sección **Evidencia fotográfica** con la
   foto, el rol que cubre, el estado y el aviso de la declaración D7.
5. Con **Verificar** la foto queda aceptada; con **Rechazar** se pide el
   motivo y la foto queda rechazada con ese texto.

## Resultado de los tests

- `npm test`: **388 passed** (366 → 388; 22 nuevos).
  - `utils/evidencia.test.js` (6): rótulos de rol y estado, tono del badge,
    marcas de observado / pendiente y opciones del filtro.
  - `stores/evidencias.test.js` (6): carga de la evidencia y descarga de las
    fotos, actualización tras verificar o rechazar, liberación de las object
    URLs al limpiar.
  - `components/registros/RecordDetailModal.evidencia.test.js` (7): la
    sección, el aviso D7, verificar, rechazar con motivo, que **el operador
    no vea los botones** y que el admin sí.
  - `stores/dashboardRegistros.test.js` (+3): el filtro de evidencia viaja al
    backend y recarga desde la primera página.
- `npm run check`: OK (build + PWA generada).
- Backend: `tests/test_dashboard_registros_evidencia.py` (7 tests) + suite
  completa OK.
- `git diff --check`: limpio.

## Capturas

`docs/screenshots/evidencia_verificacion/` (ver el README de la carpeta).

| Archivo | Qué muestra |
|---|---|
| `01-listado-filtro-1638x969.png` | Listado con el filtro de evidencia y las marcas **SIN VERIFICAR** / **OBSERVADO**. |
| `02-filtro-pendientes-1638x969.png` | Filtro *Esperando verificación* aplicado. |
| `03-detalle-evidencia-1638x969.png` | Detalle con la sección de evidencia: foto, aviso D7 y botones. |
| `04-rechazar-motivo-1638x969.png` | El rechazo pide el motivo. |
| `*-1366x768.png` | Lo mismo a 1366x768. |

## Hallazgos

1. **El aviso de la declaración D7 es lo que hace útil la foto.** Es la
   diferencia entre una foto y una foto que sirve de evidencia: el operador
   declaró que el horómetro se ve en esa pantalla, así que el encargado tiene
   que contrastarlo con la imagen. El aviso va en ámbar, arriba de los
   botones, y dice exactamente qué mirar ("si el horómetro no se ve, rechazala
   con el motivo").
2. **El rechazo pide el motivo y lo guarda.** Sin motivo no se rechaza: el
   motivo queda visible en el registro ("Motivo: ..."), que es lo que después
   lee el operador para saber qué corregir.
3. **El operador no ve los botones.** Los botones Verificar / Rechazar
   aparecen sólo para `encargado` y `admin` (D-D). El operador ve la foto y el
   estado, pero no puede cambiarlo.
4. **El listado marca el estado sin agregar columnas.** La marca va en la
   columna *Operación* ("Observado" en rojo / "Sin verificar" en ámbar): el
   dashboard ya tiene 13 columnas y sumar una más lo desbordaría a 1366px.
5. **El filtro va en el servidor.** Filtrar en el navegador solo alcanzaría la
   página cargada y el total de la paginación dejaría de cuadrar: por eso el
   backend expone `evidencia=pendiente|rechazada|sin_evidencia` y el listado
   trae por fila el resumen (total, pendientes, rechazadas).
6. **El detalle no pide la lista de evidencias si el registro no tiene fotos.**
   El backend ya dice cuántas hay (`evidencias_total`), así que el modal no
   gasta un request en la mayoría de los registros.
7. **La descarga de la foto va con el token.** El endpoint exige autenticación,
   así que un `<img src>` pelado no llegaría a la foto: el frontend baja los
   bytes con `responseType: 'blob'` y arma una object URL, que se libera al
   cerrar el modal.

## Observaciones

- La foto mostrada en la captura es una captura de pantalla del propio repo
  (es la imagen de prueba): en producción es la foto que saca el operador.
- El cuerpo del modal tiene scroll (`max-h-[72vh] overflow-y-auto`, ya
  existente): con varias fotos hay que desplazar. Es el comportamiento del
  modal de detalle, no algo de este issue.
- La marca **Observado** se aplica al registro, no a la foto: el plan define
  que la foto rechazada deja el registro observado y que el operador puede
  subir una foto nueva (D-F) sin rehacer el parte.

## Veredicto

**aprobado visualmente.**

El encargado tiene todo lo que necesita para decidir sin salir del registro: la
foto, la declaración que tiene que contrastar, el motivo de rechazo y el
listado de lo que falta revisar.
