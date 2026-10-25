# Verificación de la evidencia por el encargado (issue #204)

Capturas reales de la pantalla donde el **encargado** revisa la evidencia
fotográfica de un registro: el listado con el filtro, el detalle con la foto y
el aviso de la declaración, y el pedido de motivo al rechazar.

Se generan con la API mockeada
(`frontend/scripts/evidenciaVerificacionCapture.mjs`) y Vite. El script es
además una **verificación**: si la sección no aparece, si el encargado no ve
los botones o si algo se sale de la pantalla, sale con código de error.

## Cómo se generan

```bash
cd frontend
node scripts/evidenciaVerificacionCapture.mjs
```

Salida: `docs/screenshots/evidencia_verificacion/`.

## Qué muestra cada captura

| Archivo | Qué se ve |
|---|---|
| `01-listado-filtro-1638x969.png` | El listado con el filtro de evidencia (Todas / Esperando verificación / Con foto rechazada / Sin evidencia) y las marcas **SIN VERIFICAR** (foto pendiente) y **OBSERVADO** (foto rechazada) en la columna Operación. |
| `02-filtro-pendientes-1638x969.png` | El mismo listado con el filtro *Esperando verificación* aplicado: quedan solo los registros con fotos sin revisar. |
| `03-detalle-evidencia-1638x969.png` | El detalle del registro con la sección **Evidencia fotográfica**: la foto, el rol que cubre, el estado, el aviso ámbar de la declaración D7 y los botones **Verificar** / **Rechazar**. Abajo, la segunda foto ya verificada con quién la verificó. |
| `04-rechazar-motivo-1638x969.png` | El rechazo pide el motivo: sin motivo no se puede rechazar (la foto queda rechazada con el texto que escribe el encargado). |
| `*-1366x768.png` | Lo mismo a 1366x768. |

## Qué verifica el script

1. El filtro de evidencia aparece en el listado.
2. El registro con foto rechazada queda marcado **Observado** y el que tiene
   foto sin verificar queda marcado **Sin verificar**.
3. El filtro *Esperando verificación* deja solo los registros pendientes.
4. El detalle muestra la sección de evidencia, la foto y el aviso de la
   declaración D7.
5. El encargado (o el admin) ve los botones Verificar y Rechazar.
6. El rechazo pide el motivo.
7. **0 px de desborde** a 1638x969 y 1366x768 (lo que está dentro del área
   scrolleable del modal se cuenta aparte: es el scroll del modal, no un
   desborde del layout).

## Datos de la captura

- Usuario: **Encargado Demo** (`encargado = 1`), que es quien puede verificar
  y rechazar.
- Tipo de proceso `PROCESO`: exige foto del horómetro **y** de la pantalla del
  procesador.
- La foto cargada es un PNG real del repo
  (`01-admin-tipos-lista-1638x969.png`), servido por el mock como JPEG.
- La segunda foto está **verificada** por el encargado, para que se vea el
  contraste entre los dos estados.
