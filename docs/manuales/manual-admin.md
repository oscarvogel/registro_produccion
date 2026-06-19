<div class="cover">
  <img src="../../frontend/public/logo-forestal.png" alt="Logo Forestal">
  <h1>Manual de Usuario</h1>
  <div class="subtitle">Admin</div>
  <p class="meta">Sistema Registro Produccion Forestal<br>Version documental: Junio 2026</p>
</div>

<div class="page-break"></div>

# Manual de Usuario - Admin

## Indice

1. Alcance del rol
2. Acceso y navegacion admin
3. Inicio y panel operativo general
4. Dashboard admin
5. Gestion operativa y catalogos
6. Asignaciones operativas
7. Configuracion de acceso
8. Carga manual y pendientes globales
9. Errores frecuentes y buenas practicas

## 1. Alcance del rol

El admin tiene acceso completo a la operacion, la administracion de catalogos y la configuracion de permisos administrativos.

Como admin podes:

- Ingresar con DNI y contrasena.
- Ver el panel operativo general.
- Cargar produccion manualmente.
- Consultar dashboards operativos y ejecutivos.
- Gestionar personal, moviles, unidades de negocio, tipos de proceso, lugares de carga, predios y rodales.
- Crear, editar y eliminar asignaciones operativas.
- Habilitar o deshabilitar acceso admin a otros usuarios.
- Ver pendientes globales disponibles en el dispositivo.
- Instalar la aplicacion como PWA cuando el navegador lo permita.
- Cerrar sesion.

El sistema no permite quitarse el acceso admin a uno mismo desde `Configuracion de Acceso`.

## 2. Acceso y navegacion admin

1. Abrir la aplicacion.
2. En `Acceso operativo`, ingresar `DNI` y `Contrasena`.
3. Presionar `Ingresar`.

Si hubo cambios recientes en personal o permisos, usar `Sincronizar` en el login.

Secciones de menu disponibles:

| Seccion | Pantallas |
| --- | --- |
| `Inicio` | Panel operativo general y accesos rapidos. |
| `Operacion` | `Dashboard Operativo`, `Personal`, `Moviles`, `Asignaciones Operativas`. |
| `Catalogos` | `Unidades de Negocio`, `Tipos de Proceso`, `Lugares de Carga`, `Predios`, `Rodales`, `Configuracion de Acceso`. |
| `Produccion` | `Carga de Produccion`, `Pendientes`, `Mis Registros`. |
| `Configuracion` | Instalacion de app y cierre de sesion. |

## 3. Inicio y panel operativo general

Para usuarios admin, `Inicio` muestra el `Panel operativo general`.

Informacion principal:

- Estado `En linea` o `Sin conexion`.
- Produccion total del dia.
- Registros del dia.
- Unidades activas.
- Pendientes offline.
- Estado por unidad de negocio.
- Ultimos registros del sistema.
- Alertas operativas.
- Actividad personal del admin.

Accesos rapidos:

- `Cargar produccion`.
- `Ver pendientes`.
- `Panel admin`.
- `Mis registros`.

Las alertas pueden indicar falta de conexion, registros pendientes o unidades sin actividad.

## 4. Dashboard admin

Entrar desde `Panel admin` o la ruta admin de dashboard.

El dashboard admin muestra una vista ejecutiva para un rango de fechas.

### Filtros de periodo

Opciones rapidas:

- `Hoy`.
- `Ultimos 7 dias`.
- `Ultimos 30 dias`.
- `Este mes`.

Tambien se pueden definir fechas `Desde` y `Hasta`, y luego presionar `Actualizar`.

### Indicadores

El dashboard admin incluye:

- Produccion total.
- TN despachadas.
- Combustible total.
- Registros.
- Unidades con actividad.
- Operadores activos.
- Equipos activos.
- Comparativa contra periodo anterior.
- Evolucion diaria.
- Ranking de unidades por produccion.
- Produccion por proceso.
- Ultimos registros productivos.

Si no hay datos, ampliar el rango de fechas o revisar que existan registros cargados.

## 5. Gestion operativa y catalogos

Las pantallas de gestion comparten una estructura:

- Encabezado con cantidad de registros.
- Boton `Refrescar`.
- Boton `Nuevo`, excepto en `Asignaciones Operativas`, donde el flujo principal usa el panel rapido.
- Busqueda.
- Filtro por unidad cuando aplica.
- Tabla en escritorio y tarjetas en movil.
- Acciones `Editar` y `Eliminar`.
- Paginacion con selector `Ver`.

### Personal

Permite administrar usuarios operativos.

Campos principales:

- Nombre.
- DNI.
- Contrasena.
- Activo.
- Encargado.
- Acceso admin.
- Unidad principal.
- Unidades vinculadas.
- Tipo de proceso.

Reglas importantes:

- `Nombre` es obligatorio.
- Debe seleccionarse al menos una unidad vinculada.
- Si se edita un usuario y se deja la contrasena vacia, no se cambia la contrasena existente.

### Moviles

Permite administrar equipos o maquinas.

Campos principales:

- Patente.
- Detalle.
- Unidad de negocio.
- Activo.

Regla importante:

- `Patente` y `Detalle` son obligatorios.

### Unidades de Negocio

Permite administrar unidades. En esta pantalla esta disponible la accion `Relaciones`, que muestra vinculaciones con:

- Personal.
- Moviles.
- Procesos.

Usar esta vista para revisar rapidamente que una unidad tenga los elementos necesarios para operar.

### Tipos de Proceso

Permite administrar procesos disponibles para la carga.

Campos principales:

- Nombre.
- Activo.
- Unidades habilitadas.
- Requiere Acta.
- Requiere Predio.
- Requiere Rodal.

Regla importante:

- `Nombre` es obligatorio.

La vinculacion con unidades controla que procesos aparecen al cargar produccion o al filtrar dashboards.
Los requisitos `Acta`, `Predio` y `Rodal` controlan que campos de ubicacion se muestran y se exigen en la carga de produccion. Para crear un proceso nuevo, activar solo los datos que correspondan a la operacion; si los tres quedan desactivados, la carga no pedira ubicacion operativa.

### Lugares de Carga

Permite administrar lugares disponibles por unidad de negocio.

Campos principales:

- Descripcion.
- Unidad de negocio.
- Activo.

### Predios

Permite administrar predios usados en la ubicacion de la carga.

Campos principales:

- Nombre.
- Datos tecnicos que correspondan al catalogo.

### Rodales

Permite administrar rodales asociados a predios.

Campos principales:

- Rodal.
- Predio.
- VAM.
- Tarifa.
- Extraccion.
- Carga.

Los rodales se usan al completar `Ubicacion y Referencia` en la carga de produccion.

## 6. Asignaciones operativas

Entrar desde `Operacion > Asignaciones Operativas`.

La pantalla incluye un panel rapido para asignar:

1. `Unidad de Negocio`.
2. `Chofer`.
3. `Movil`.
4. `Tipo de Proceso`.
5. Presionar `Asignar`.

El sistema filtra choferes, moviles y procesos segun la unidad seleccionada.

Validaciones principales:

- Deben completarse movil, chofer y tipo de proceso.
- El chofer debe pertenecer a la unidad del movil.
- El tipo de proceso debe estar habilitado para la unidad del movil.
- No se permite crear una asignacion duplicada.

Tambien se puede editar o eliminar asignaciones existentes desde la tabla.

## 7. Configuracion de acceso

Entrar desde `Catalogos > Configuracion de Acceso`.

Esta pantalla permite habilitar o deshabilitar `Acceso Admin` para otros usuarios.

Uso:

1. Buscar el usuario por nombre o DNI.
2. Revisar columnas `Activo`, `Encargado` y `Acceso Admin`.
3. Activar o desactivar el checkbox de acceso admin.
4. Esperar el estado `Guardando...` y confirmar que quede `Habilitado` o `Deshabilitado`.

Restriccion:

- No podes quitarte tu propio acceso admin. El checkbox del usuario actual aparece deshabilitado.

## 8. Carga manual y pendientes globales

### Carga de Produccion

El admin puede usar `Produccion > Carga de Produccion` para registrar una carga manual.

El formulario mantiene los mismos 9 pasos:

1. Contexto.
2. Operador.
3. Equipo.
4. Proceso.
5. Tiempo.
6. Produccion.
7. Consumos.
8. Ubicacion.
9. Revision.

Como admin, revisar especialmente unidad, operador, equipo y proceso antes de guardar, ya que una carga manual puede afectar reportes globales.

### Pendientes

Entrar desde `Produccion > Pendientes`.

Para admin, la pantalla muestra la cola global visible en el dispositivo.

Acciones disponibles:

- `Refrescar`.
- `Sincronizar`.
- `Reintentar`.
- `Ver detalle`.
- `Eliminar`.

Los indicadores muestran pendientes y fallidos del sistema visibles localmente.

<div class="warning">
La cola de pendientes es local al dispositivo. Un admin ve los registros disponibles en ese equipo, no necesariamente todos los pendientes existentes en otros dispositivos.
</div>

### Mis Registros

El admin tambien puede consultar `Mis Registros` para ver actividad cargada por su propio usuario.

## 9. Errores frecuentes y buenas practicas

| Situacion | Que hacer |
| --- | --- |
| No aparece un usuario, movil o proceso | Revisar filtros de busqueda y unidad. Usar `Refrescar`. |
| No se puede guardar personal | Verificar nombre y al menos una unidad vinculada. |
| No se puede guardar movil | Completar patente y detalle. |
| Asignacion rechazada | Revisar que chofer, movil y proceso pertenezcan o esten habilitados para la misma unidad. |
| Dashboard sin datos | Ampliar rango de fechas o revisar que existan registros en el periodo. |
| Usuario sin acceso esperado | Revisar `Configuracion de Acceso`, estado activo y permisos de encargado/admin. |
| Pendientes fallidos | Usar `Ver detalle`, revisar error y reintentar. |

Buenas practicas:

- Crear o revisar primero unidades, procesos, moviles y personal antes de configurar asignaciones.
- Mantener vinculaciones de unidades consistentes para evitar listas vacias en carga.
- Usar `Relaciones` en unidades para auditar configuracion.
- No eliminar registros pendientes sin confirmar que no deben enviarse.
- Evitar cambiar accesos admin sin validar quien necesita operar la administracion.
- Cerrar sesion al terminar si el dispositivo es compartido.
