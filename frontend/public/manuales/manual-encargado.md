<div class="cover">
  <img src="../../frontend/public/logo-forestal.png" alt="Logo Forestal">
  <h1>Manual de Usuario</h1>
  <div class="subtitle">Encargado</div>
  <p class="meta">Sistema Registro Producción Forestal<br>Versión documental: Junio 2026</p>
</div>

<div class="page-break"></div>

# Manual de Usuario - Encargado

## Indice

1. Alcance del rol
2. Acceso y navegacion
3. Inicio operativo
4. Carga de Produccion
5. Dashboard Operativo
6. Registros Pendientes por unidad
7. Configuracion, instalacion y salida
8. Errores frecuentes y buenas practicas

## 1. Alcance del rol

El encargado registra produccion y consulta informacion operativa de sus unidades asignadas. A diferencia del operador, puede seleccionar operadores en la carga y acceder al `Dashboard Operativo`.

Como encargado podes:

- Ingresar con DNI y contrasena.
- Registrar cargas de produccion.
- Seleccionar el operador de la carga dentro de tus unidades disponibles.
- Consultar dashboard operativo con filtros por unidad, proceso, maquina y fechas.
- Ver evolucion diaria, ranking de maquinas y metricas de combustible.
- Revisar registros pendientes o fallidos de tus unidades asignadas.
- Instalar la aplicacion como PWA cuando el navegador lo permita.
- Cerrar sesion.

No corresponde al rol encargado:

- Administrar catalogos.
- Crear o modificar personal, moviles, unidades, procesos, predios o rodales.
- Cambiar permisos de acceso admin.
- Ver el panel admin global.

## 2. Acceso y navegacion

1. Abrir la aplicacion.
2. En `Acceso operativo`, ingresar `DNI` y `Contrasena`.
3. Presionar `Ingresar`.

Si hubo cambios recientes en usuarios o permisos, usar `Sincronizar` desde el login antes de ingresar.

Pantallas disponibles:

| Pantalla | Uso principal |
| --- | --- |
| `Inicio` | Resumen diario y accesos rapidos. |
| `Dashboard Operativo` | Analisis de produccion, combustible, rankings y evolucion. |
| `Carga de Produccion` | Alta guiada de registros, con seleccion de operador. |
| `Pendientes` | Cola de registros pendientes o fallidos de unidades asignadas. |
| `Configuracion` | Instalacion de app y cierre de sesion. |

La etiqueta del usuario muestra `Encargado`. Si aparece la franja `Sin conexion`, las cargas nuevas quedan guardadas localmente.

## 3. Inicio operativo

La pantalla `Inicio` resume la actividad del dia:

- Estado `En linea` o `Sin conexion`.
- Produccion del dia.
- Horas trabajadas.
- Registros cargados.
- Combustible.
- Ultimo registro.
- Cantidad de pendientes.

Accesos rapidos habituales:

- `Carga de Produccion`.
- `Registros pendientes`.
- `Dashboard`.
- `Instalar app`, cuando este disponible.

## 4. Carga de Produccion

Entrar desde `Inicio` o desde `Produccion > Carga de Produccion`.

El formulario usa 9 pasos. Para guardar, cada paso requerido debe estar completo.

### Paso 1: Contexto

Completar:

- `Fecha`.
- `Unidad de Negocio`.

La unidad elegida define que operadores, moviles, procesos y lugares de carga quedan disponibles.

### Paso 2: Operador

Como encargado, el campo `Seleccionar Operador` esta habilitado.

1. Elegir la unidad de negocio en el paso anterior.
2. Buscar el operador por nombre.
3. Seleccionar el operador correcto.

Al seleccionar el operador, el sistema consulta sus asignaciones y puede sugerir maquina y proceso.

### Paso 3: Equipo / Maquinaria

Opciones disponibles:

- Seleccionar una opcion de `Asignaciones del operador`.
- Buscar maquina por numero, marca, detalle o patente.
- Cambiar la maquina seleccionada con `Cambiar`.

Si no aparece una maquina esperada, revisar que la unidad sea correcta y que el operador tenga asignacion o que la maquina pertenezca a esa unidad.

### Paso 4: Proceso / Actividad

Seleccionar `Tipo de Proceso`. La lista depende de la unidad de negocio.

El proceso define que campos se pediran en `Datos de Produccion`.

### Paso 5: Control de Tiempo

Completar:

- `Hora Inicio`.
- `Hora Fin`.
- `Hs No Operativas`, si corresponde.
- Motivo de horas no operativas.

El sistema valida que las horas sean mayores a 0, que el fin no sea menor que el inicio y que la hora inicial no contradiga el ultimo fin registrado para la maquina.

### Paso 6: Datos de Produccion

Completar los campos productivos visibles. Pueden incluir:

- Toneladas despachadas.
- Carros.
- Distancia recorrida.
- Metros cubicos.
- Plantas.
- Hectareas.
- Kilometros.
- Horas a disposicion.
- Campos de pies y pulpable para procesos de corte.

Los campos requeridos deben tener valores mayores a 0.

### Paso 7: Consumos

Registrar combustible y aceites cuando correspondan.

Si el proceso incluye sistema de corte, completar los datos solicitados de espada, puntera, cadena, pinon o cantidad de cadenas segun aplique.

### Paso 8: Ubicacion y Referencia

Completar:

- `Lugar de Carga`, si existe para la unidad.
- `Acta`.
- `Predio`.
- `Rodal` o `Rodal manual`.
- `Observaciones`, si corresponde.

El sistema no guarda si la ubicacion requerida esta incompleta.

### Paso 9: Revision y Confirmacion

Revisar cuidadosamente:

- Fecha y unidad.
- Operador seleccionado.
- Equipo.
- Proceso.
- Horario.
- Produccion.
- Ubicacion.

Si algun dato no corresponde, volver y corregirlo antes de guardar. Esta revision es especialmente importante cuando el encargado carga datos de otro operador.

### Guardar borrador

`Guardar borrador` conserva la carga en el dispositivo. Usarlo para interrupciones temporales; no reemplaza el guardado final.

## 5. Dashboard Operativo

Entrar desde `Operacion > Dashboard Operativo` o desde el acceso rapido `Dashboard`.

El dashboard permite consultar produccion y consumo de las unidades disponibles para el encargado.

### Filtros principales

| Filtro | Descripcion |
| --- | --- |
| `Unidad de Negocio` | Unidad a consultar. Para encargado, solo se muestran unidades asignadas. |
| `Tipo de Proceso` | Limita indicadores al proceso seleccionado. |
| `Maquina / Equipo` | Filtra por movil especifico. |
| `Desde` y `Hasta` | Rango de fechas del analisis. |
| `Limpiar filtros` | Vuelve a una consulta sin filtros adicionales. |

En dispositivos moviles, usar el boton `Filtros` para abrir o cerrar la zona de filtros.

### Indicadores y graficos

El dashboard muestra:

- KPI principal de produccion.
- KPIs secundarios segun datos disponibles.
- Variacion porcentual contra periodo anterior cuando aplica.
- `Evolucion diaria` de produccion.
- `Combustible - Evolucion diaria`.
- `Ranking de Maquinas`.

### Ranking de Maquinas

El ranking permite comparar maquinas por:

- `Produccion`.
- `Combustible`.

Tambien puede filtrarse por `Tipo de Proceso` dentro del ranking.

### Sin datos

Si aparece `No hay datos para los filtros seleccionados`, ampliar fechas o quitar filtros. Si aparece `Sin unidades disponibles`, cerrar sesion y volver a ingresar para refrescar permisos; si persiste, solicitar revision de accesos.

## 6. Registros Pendientes por unidad

Entrar desde `Produccion > Pendientes`.

Para encargado, la pantalla muestra registros pendientes o fallidos asociados a sus unidades de negocio asignadas.

Indicadores principales:

- Pendientes locales.
- Fallidos locales.
- Pendientes de unidad.
- Fallidos de unidad.

Acciones:

- `Refrescar`: actualiza la vista.
- `Sincronizar`: intenta enviar pendientes visibles.
- `Reintentar`: reenvia un registro puntual.
- `Ver detalle`: permite revisar el payload local.
- `Eliminar`: descarta el registro local.

<div class="warning">
Eliminar un pendiente es una accion definitiva sobre la cola local del dispositivo. Confirmar antes de hacerlo.
</div>

## 7. Configuracion, instalacion y salida

En `Configuracion`:

- Usar `Instalar App` si el navegador ofrece instalacion PWA.
- Usar `Cerrar sesion` al finalizar el trabajo o si el dispositivo es compartido.

Tambien se puede cerrar sesion desde el menu lateral o encabezado movil.

## 8. Errores frecuentes y buenas practicas

| Situacion | Que hacer |
| --- | --- |
| No aparece un operador | Revisar la unidad seleccionada. El listado depende de la unidad. |
| No aparece una maquina | Confirmar unidad y asignaciones. Buscar por patente o detalle. |
| No aparecen procesos | Verificar que la unidad tenga tipos de proceso habilitados. |
| Dashboard sin datos | Ampliar fechas o quitar filtros. |
| Registro pendiente fallido | Abrir `Ver detalle`, revisar error y usar `Reintentar`. |
| Carga sin conexion | Guardar normalmente; la aplicacion sincronizara al reconectar. |

Buenas practicas:

- Seleccionar primero la unidad correcta.
- Verificar operador y maquina antes de avanzar.
- Revisar el resumen final antes de guardar.
- Usar filtros del dashboard para acotar el analisis, no para corregir datos cargados.
- Evitar eliminar pendientes sin confirmar que no deben enviarse.
