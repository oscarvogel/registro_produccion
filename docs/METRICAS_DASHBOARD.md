# Catálogo inicial de métricas y dashboards

Documento de trabajo para `Analytics & Reporting`. Describe el comportamiento
implementado y establece criterios para futuras métricas, muestreos y cambios
de visualización.

## Alcance actual

El Dashboard Operativo calcula sobre el conjunto completo de registros que
cumplen los filtros seleccionados. Actualmente no aplica muestreo estadístico.
Los filtros disponibles son:

- unidad de negocio;
- tipo de proceso u operación;
- máquina/equipo;
- fecha desde y hasta.

La fuente de datos principal es `tablero_produccion`. Las definiciones
configurables se almacenan en `kpi_definicion` y su asociación a procesos en
`tipo_proceso_kpi`.

## Definición mínima de una métrica

Antes de agregar una métrica nueva debe documentarse:

| Campo | Requerido |
|---|---|
| Nombre visible | Sí |
| Pregunta que responde | Sí |
| Fórmula y agregación | Sí |
| Unidad de medida | Sí |
| Granularidad | Sí: registro, jornada, día, equipo o unidad |
| Filtros y alcance | Sí |
| Registros incluidos/excluidos | Sí |
| Fuente y fecha de actualización | Sí |
| Responsable funcional | Sí |
| Objetivo o umbral | Cuando sea un KPI |
| Interpretación de variaciones | Sí |

Si no existe objetivo, umbral o decisión asociada, la tarjeta debe tratarse
como métrica y no como KPI.

## Métricas implementadas

### Métricas configurables por proceso

| Métrica | Campo/agregación actual | Unidad | Interpretación |
|---|---|---:|---|
| Toneladas despachadas | `SUM(tn_despachadas)` | TN | Total despachado en el alcance seleccionado |
| Metros cúbicos | `SUM(m3)` | M³ | Total procesado |
| Plantas procesadas | `SUM(plantas)` | uds | Cantidad procesada |
| Carros | `SUM(carros)` | uds | Cantidad de carros registrada |
| Metros recorridos | `SUM(mtrs_recorridos)` | mts | Distancia registrada |
| KM carreteo | `SUM(km_carreteo)` | km | Distancia total de carreteo |
| KM perfilado | `SUM(km_perfilado)` | km | Distancia total de perfilado |
| Hectáreas | `SUM(has)` | HAS | Superficie trabajada |
| Horas disposición | `SUM(hr_disposicion)` | hs | Horas de disposición |
| Combustible consumido | `SUM(combustible)` | lts | Litros registrados |
| Horas no operativas | `SUM(hrs_no_op)` | hs | Tiempo no operativo registrado |
| Horas trabajadas | cálculo custom | hs | Suma deduplicada de `hr_fin - hr_inicio` por jornada |
| Eficiencia operativa | cálculo custom | % | `(horas trabajadas - horas no operativas) / horas trabajadas * 100` |
| Registros del período | `COUNT(id)` | reg | Cantidad de filas incluidas |
| Horas de remolque | `SUM(hr_remolque)` | hs | Horas de remolque acumuladas |

Las horas trabajadas y la eficiencia no se calculan como una suma ciega por
fila: las filas hermanas con `form_uuid` se agrupan como una jornada y se
deduplican los valores de cabecera.

### Métricas de administración

El Análisis de Producción agrega además:

- registros del período;
- producción total;
- toneladas despachadas;
- combustible total;
- unidades activas;
- operadores activos;
- equipos activos;
- variación contra el período anterior equivalente;
- participación porcentual de producción por unidad;
- evolución diaria de producción y cantidad de registros.

La variación porcentual se calcula como:

```text
(valor actual - valor del período anterior) / valor del período anterior * 100
```

Cuando el período anterior vale cero, la variación queda sin valor para no
representar una comparación inválida.

## Clasificación funcional

### Operación

Pregunta principal: **¿qué está ocurriendo en la operación seleccionada?**

Debe concentrar métricas de seguimiento por unidad, proceso, equipo y período:

- métrica principal del proceso;
- horas trabajadas;
- eficiencia operativa;
- combustible;
- registros;
- evolución diaria;
- ranking de equipos.

### Análisis de Producción

Pregunta principal: **¿qué tendencias y diferencias sirven para gestionar la
producción?**

Debe concentrar:

- comparación entre períodos;
- comparación entre unidades;
- comparación entre procesos;
- evolución productiva;
- participación por unidad o proceso;
- indicadores normalizados, cuando sus unidades y denominadores estén
  validados.

### Inicio

Pregunta principal: **¿qué necesito consultar o hacer rápidamente?**

Debe mostrar un resumen breve, accesos frecuentes, actividad y estado de
sincronización. No debe replicar el análisis completo de los dashboards.

## Criterio de muestreo

El muestreo no reemplazará los totales operativos cuando la base completa esté
disponible.

Si se necesita una muestra para auditoría, control de calidad o análisis
exploratorio, debe definirse explícitamente:

- población objetivo;
- unidad de selección;
- período;
- estratos: unidad, proceso, equipo y fecha, según la pregunta;
- método aleatorio o sistemático con inicio aleatorio;
- tamaño y justificación;
- semilla o criterio reproducible;
- cobertura y limitaciones;
- margen de error o intervalo de confianza cuando se hagan inferencias.

Nunca se debe mostrar una métrica calculada sobre una muestra como si fuera el
total real sin indicar `N` de población, `n` de muestra y método utilizado.

## Gaps identificados antes de ampliar el Dashboard

La implementación actual todavía no expone en el contrato de métricas:

- cantidad de registros incluidos (`N`) junto con cada respuesta;
- cobertura o completitud de datos;
- fecha/hora de actualización del cálculo;
- objetivo y umbral de cada KPI;
- definición funcional visible de cada fórmula;
- indicadores normalizados como productividad o consumo específico.

Estos datos deben definirse funcionalmente antes de agregarse al backend. El
frontend no debe reconstruir fórmulas de negocio ni convertirse en una segunda
fuente de verdad.

## Perfilado local de consistencia

Se realizó un perfilado de solo lectura sobre la base local. Este apartado es
un diagnóstico técnico, no una regla de negocio ni una migración de datos.

Hallazgos:

- `tablero_produccion` contiene 27.180 registros y 5.594 tienen `cod_un` no
  nulo, que es el alcance actualmente consultable por unidad en el Dashboard.
- Solo hay registros con `tipo_proceso_id` asociado para `PROCESO` y
  `PERFILADO` en la configuración local. El resto de las operaciones aparece
  como texto en `operacion` y se ofrece como filtro histórico.
- Cuando se filtra por una operación textual sin `tipo_proceso_id`, el código
  actual reutiliza la configuración de KPI disponible para la unidad. Esto
  puede mostrar una métrica configurada para otro proceso y requiere validación
  funcional antes de presentarse como KPI.
- Hay un registro con `hr_fin < hr_inicio` y 145 registros con ambos valores
  iguales dentro del conjunto con unidad. La fórmula actual conserva
  `hr_fin - hr_inicio`; no se modificó porque la decisión sobre datos inválidos
  o jornadas sin avance debe ser funcional.
- En los registros tipados como `PROCESO`, `m3` y `produccion` tienen valores,
  mientras que `tn_despachadas` no presenta valores positivos. En `PERFILADO`,
  la métrica con mayor cobertura es `km_perfilado`. Esto confirma que las
  métricas deben validarse por proceso y no mostrarse como un conjunto
  universal.
- `Horas Remolque` existe como definición de métrica, pero no aparece asociada
  a un proceso en la configuración local de `tipo_proceso_kpi`.

### Decisiones pendientes

Antes de modificar fórmulas o contratos se debe confirmar:

1. qué operación textual corresponde a cada métrica cuando falta
   `tipo_proceso_id`;
2. si un delta de horómetro negativo es error, reinicio del contador o dato a
   excluir;
3. si un delta cero representa una jornada válida;
4. qué unidad de producción corresponde a cada proceso;
5. qué procesos deben mostrar `Horas Remolque`;
6. qué objetivos o umbrales convierten una métrica en KPI.

Hasta resolver estas preguntas, las métricas deben seguir tratándose como
datos descriptivos del alcance seleccionado y no como indicadores gerenciales
comparables entre procesos.

## Criterios para futuros gráficos

- líneas para evolución temporal;
- barras para comparar unidades, procesos o equipos;
- tablas para valores exactos y exportación;
- filtros visibles y resumen del alcance activo;
- colores consistentes por métrica;
- ningún estado comunicado únicamente por color;
- explicación de datos faltantes, cobertura y fecha de actualización;
- paginación para tablas grandes y sin scroll horizontal en móvil.

## Fuentes consultadas

- [NIST: Define Sampling Plan](https://www.itl.nist.gov/div898/handbook/ppc/section3/ppc33.htm)
- [Penn State: Sampling](https://online.stat.psu.edu/stat507/Lesson02)
- [Penn State: Confidence Intervals and Sample Size](https://online.stat.psu.edu/stat506/Lesson02)
- [GOV.UK: How to set performance metrics](https://www.gov.uk/service-manual/measuring-success/how-to-set-performance-metrics-for-your-service)
- [ONS: Dashboards](https://service-manual.ons.gov.uk/data-visualisation/guidance/dashboards)
- [Government Analysis Function: Testing dashboards](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-testing-dashboards-for-design-and-accessibility/)
- [Microsoft: KPI visuals](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-kpi)
