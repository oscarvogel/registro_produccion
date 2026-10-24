# Modo offline de la evidencia (issue #202)

Capturas reales del circuito **offline** de la evidencia fotográfica: el
operador toma la foto, guarda el parte sin señal, y la foto sube **antes** que
el parte cuando vuelve la conexión.

Se generan con la API mockeada (`frontend/scripts/evidenciaOfflineSmoke.mjs`)
y Vite. El script es además un **smoke E2E**: si el orden de las subidas o el
estado de la cola no son los esperados, sale con código de error.

## Cómo se generan

```bash
cd frontend
node scripts/evidenciaOfflineSmoke.mjs
```

Salida: `docs/screenshots/evidencia_offline/`.

## Qué muestra cada captura

| Archivo | Qué se ve |
|---|---|
| `01-evidencia-con-foto-1638x969.png` | Paso **Evidencia** del wizard con la foto de la pantalla del procesador cargada y la declaración de D7 tildada (*"En esa misma pantalla se ve el horómetro"*): con esa sola foto se cubren los dos roles. |
| `01b-paso-revision-1638x969.png` | El paso **Revisión** (10 de 10): los pasos anteriores quedan en `VALIDADO` y el botón *Guardar Registro* está disponible. |
| `02-guardado-sin-conexion-1638x969.png` | Sin conexión, el registro **no se bloquea**: se avisa *"Guardado solo en este teléfono"* y el parte queda en la cola local. La franja superior dice *"Sin conexión"*. |
| `03-pendientes-foto-en-espera-1638x969.png` | La pantalla **Registros Pendientes** con el badge azul *"1 foto(s) adjunta(s), esperando subir"*: el operador ve que la foto sigue en el teléfono y no en el servidor. |
| `04-pendientes-tras-sincronizar-1638x969.png` | Después del sync: *"Todo sincronizado"*, cola vacía y contadores en 0. La pantalla se refresca sola cuando el store sincroniza. |

## Qué verifica el smoke

1. El wizard llega al paso de evidencia con la foto y la declaración.
2. **Sin conexión no se intenta enviar nada**: el mock aborta los `POST` de
   producción en esa fase y el smoke falla si alguno sale.
3. La foto queda en la base local del teléfono (`pendingEvidencias`, con el
   `Blob` crudo) junto con el parte, y los dos comparten el `form_uuid`.
4. Al volver la conexión el orden es **`/api/produccion/evidencias` →
   `/api/produccion/`**, y el parte lleva `evidencias: [id]`.
5. Tras el sync el parte sale de la cola y la foto queda marcada como subida.

Salida esperada de la última corrida:

```
1. wizard completo hasta el paso Evidencia con la foto y la declaracion D7
2. sin conexion el registro se guardo en el telefono
3. cola local -> evidencias: 1 (blob 90616 bytes, synced 0) | registros: 1
4. sin conexion NO se intentó enviar ni la foto ni el parte
5. pantalla Pendientes -> badge: "1 foto(s) adjunta(s), esperando subir"
6. orden de las llamadas -> /api/produccion/evidencias -> /api/produccion/
7. la foto se subio antes que el parte (orden correcto)
8. el parte lleva evidencias=[77] (id 77)
9. cola local tras sincronizar -> evidencias: 1 (synced 1) | registros: 0
```

## Datos de la captura

- Tipo de proceso `PROCESO`: exige foto del horómetro **y** de la pantalla del
  procesador (configuración inicial de la decisión D8).
- La foto cargada es un PNG real del repo (`01-admin-tipos-lista-1638x969.png`),
  comprimido por el navegador a JPEG (lado mayor 1600 px) como en el formulario
  real: encolada quedó en **90 616 bytes**.
- Resolución: **1638x969**, la pantalla del cliente. El resto de las pantallas
  con evidencia ya tienen su propia revisión visual (`evidencia_form/`).
