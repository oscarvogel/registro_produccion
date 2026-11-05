# Movimiento único de combustible

## Decisión

Desde la corrección de la issue #105, cada abastecimiento físico crea un solo
movimiento de egreso en `cargacomb`, desde el flujo donde se origina:

- `POST /api/produccion/` registra el parte y su egreso de combustible en la
  misma transacción cuando los litros son mayores que cero. El movimiento queda
  vinculado con `tabla = tablero_produccion` e `idtabla = <id del parte>`.
- `POST /api/combustible/cargas` registra abastecimientos sin parte de
  producción y usa `tabla = carga_combustible`.

La misma carga física no debe ingresarse en ambos formularios.

## Contrato del movimiento

- Identidad estable `form_uuid`, reutilizada en los reintentos.
- Equipo, fecha y litros.
- Kilometraje u horómetro real, mayor que cero.
- `id_lugar_carga` e `id_tipo_comb`.
- `remito` obligatorio y hasta dos remitos adicionales.

En Producción, la identidad del parte evita recrear tanto el parte como su
movimiento en un reintento. En cargas independientes, la combinación
`(personal, form_uuid)` es única. Dos cargas reales con igual equipo, fecha y
litros deben usar identidades distintas y se guardan como movimientos separados.

Si una integración transfiere un abastecimiento entre ambos endpoints, debe
conservar el mismo `form_uuid`: el segundo envío recupera el movimiento
existente y no crea otro. La interfaz normal no transfiere cargas; dirige cada
evento al formulario correspondiente según tenga o no un parte de producción.

## Fuente de verdad en la UI operativa

La tarjeta **Combustible del equipo** de Registro Producción y el **Control de
combustible** de Forestal leen el mismo libro: `cargacomb`.

- La app suma todos los egresos del equipo en el período: partes, cargas
  independientes y cargas manuales o importadas.
- El consumo por hora usa las horas de todos los partes del equipo, no solo las
  del operador que está mirando la pantalla.
- El campo `tablero_produccion.combustible` queda como dato declarado del parte
  y no se usa para el KPI de combustible.
- El detalle de cada parte muestra los litros del movimiento vinculado por
  `tabla = 'tablero_produccion'`/`'PRODUCCION'` e `idtabla = <id del parte>`.
  Así el mismo remito nunca muestra dos valores distintos entre la app y
  Forestal.

## Datos históricos

La migración `20260730_cargacomb_form_uuid.sql` agrega solamente la identidad
idempotente para movimientos nuevos. No modifica, combina ni elimina registros
históricos. Cualquier saneamiento de duplicados existentes requiere una tarea
separada, una consulta previa de sólo lectura y aprobación explícita.
