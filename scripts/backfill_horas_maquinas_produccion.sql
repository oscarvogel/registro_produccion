-- Issue #146
-- Completa produccion historica SOLO para registros HORAS MAQUINAS
-- que quedaron en 0/NULL y poseen horometros validos.
--
-- Recomendado: ejecutar primero el SELECT de control y revisar la cantidad.

SELECT
    id,
    fecha,
    UN,
    equipo,
    operador,
    hr_inicio,
    hr_fin,
    produccion AS produccion_actual,
    ROUND(hr_fin - hr_inicio, 2) AS produccion_calculada
FROM tablero_produccion
WHERE UPPER(TRIM(operacion)) = 'HORAS MAQUINAS'
  AND (produccion IS NULL OR produccion = 0)
  AND hr_inicio > 0
  AND hr_fin > hr_inicio
ORDER BY fecha, id;

START TRANSACTION;

UPDATE tablero_produccion
SET produccion = ROUND(hr_fin - hr_inicio, 2),
    unidad_produccion = 'HS'
WHERE UPPER(TRIM(operacion)) = 'HORAS MAQUINAS'
  AND (produccion IS NULL OR produccion = 0)
  AND hr_inicio > 0
  AND hr_fin > hr_inicio;

-- Revisar ROW_COUNT() antes de confirmar.
SELECT ROW_COUNT() AS registros_actualizados;

-- Cambiar por ROLLBACK si la cantidad no coincide con lo esperado.
COMMIT;
