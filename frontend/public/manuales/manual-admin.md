<div class="cover">
  <img src="../../frontend/public/logo-forestal.png" alt="Logo Forestal">
  <h1>Manual de Usuario</h1>
  <div class="subtitle">Admin</div>
  <p class="meta">Sistema Registro Producción Forestal<br>Versión documental: Agosto 2026</p>
</div>

<div class="page-break"></div>

# Manual de Usuario - Admin

## Índice

1. Alcance, acceso y navegación
2. Inicio y dashboards
3. Centro administrativo y catálogos
4. Asignaciones operativas
5. Configuración de acceso
6. Carga manual, offline y Pendientes
7. Errores frecuentes y buenas prácticas

## 1. Alcance, acceso y navegación

El rol admin puede operar, consultar dashboards, administrar catálogos y configurar accesos administrativos. No permite quitarse el acceso admin a sí mismo desde `Configuración de acceso`.

![Login admin](/manuales/capturas/admin/01-login.png)

Para ingresar:

1. Abrí la aplicación.
2. Completá `DNI` y `Contrasena`.
3. Presioná `Sincronizar` si hubo cambios de usuarios, permisos o catálogos.
4. Presioná `Ingresar`.

![Menú móvil admin](/manuales/capturas/admin/04-menu-movil.png)

En la navegación móvil están disponibles `Inicio`, `Manuales`, `Administración`, `Operación`, `Combustible`, `Producción`, `Pendientes`, `Mis Registros`, `Configuración` y `Salir`. Abrí el panel con `Abrir navegacion` y cerralo con `Cerrar menu`.

## 2. Inicio y dashboards

![Inicio admin](/manuales/capturas/admin/03-inicio.png)

`Inicio` muestra el panel operativo general: estado de conexión, producción del período, registros, unidades con actividad, pendientes offline, actividad por unidad y últimos registros. Los accesos rápidos permiten abrir `Dashboard`, `Carga de Producción`, `Carga de Combustible`, `Pendientes` y `Panel Admin`.

### Dashboard Producción

![Dashboard Producción](/manuales/capturas/admin/16-admin-dashboard.png)

Entrá desde `Operación > Dashboard Producción` o desde el acceso rápido. Elegí un período con `Hoy`, `Últimos 7 días`, `Últimos 30 días` o `Este mes`, o definí `Desde` y `Hasta`. Presioná `Actualizar`.

El panel muestra producción total, toneladas, combustible, registros, unidades con actividad, operadores, equipos, comparativa con el período anterior, evolución diaria, ranking de unidades, procesos y últimos registros. Si no hay datos, ampliá el período o verificá que existan cargas en el rango.

### Dashboard Operativo

Desde `Operación > Dashboard Operativo` consultá indicadores por unidad, tipo de proceso y máquina. En el teléfono el botón `Filtros` abre la zona de filtros. `Limpiar` quita las selecciones adicionales.

## 3. Centro administrativo y catálogos

![Centro administrativo](/manuales/capturas/admin/15-admin-centro.png)

Entrá desde `Administración`. El centro se organiza en `Personas y equipos`, `Configuración productiva` y `Seguridad`.

### Personas y equipos

- `Personal`: usuarios, roles y relaciones operativas.
- `Móviles`: equipos, unidades y datos técnicos.
- `Asignaciones operativas`: vínculos entre choferes, móviles y procesos.

Las pantallas usan búsqueda, filtros, `Refrescar`, `Nuevo` cuando corresponde y acciones `Editar` y `Eliminar`. En móvil las tablas se muestran en tarjetas o requieren desplazamiento horizontal según la pantalla.

### Configuración productiva

- `Unidades de negocio`: estructura operativa y `Relaciones`.
- `Tipos de proceso`: procesos, unidades habilitadas y requisitos de carga.
- `Lugares de carga`: puntos disponibles por unidad.
- `Predios`: predios disponibles para producción.
- `Rodales`: rodales y valores productivos.
- `Actas`: actas habilitadas para registrar producción.

En `Tipos de proceso`, `Nombre` es obligatorio. Las opciones `Requiere Acta`, `Requiere Predio` y `Requiere Rodal` determinan qué aparece y qué se exige en `Ubicación y Referencia`. La vinculación con unidades controla la lista visible en la carga y los dashboards.

En `Personal`, verificá nombre y al menos una unidad vinculada. Si editás una persona y dejás la contraseña vacía, la contraseña existente no cambia. En `Móviles`, `Patente` y `Detalle` son obligatorios.

## 4. Asignaciones operativas

Entrá desde `Administración > Asignaciones operativas`. En el panel rápido seleccioná:

1. `Unidad de Negocio`.
2. `Chofer`.
3. `Movil`.
4. `Tipo de Proceso`.
5. Presioná `Asignar`.

El sistema filtra los listados según la unidad. El chofer debe pertenecer a la unidad del móvil, el proceso debe estar habilitado para esa unidad y no se permite crear una asignación duplicada. Revisá la tabla para editar o eliminar una asignación existente.

## 5. Configuración de acceso

![Configuración de acceso](/manuales/capturas/admin/17-configuracion-acceso.png)

Entrá desde `Administración > Configuración de acceso`.

1. Buscá por nombre o DNI.
2. Revisá `Activo`, `Encargado` y `Acceso Admin`.
3. Activá o desactivá el checkbox de `Acceso Admin` para otro usuario.
4. Esperá `Guardando...` y confirmá `Habilitado` o `Deshabilitado`.

El checkbox del usuario actual está deshabilitado. No intentes quitarte el acceso admin a vos mismo.

## 6. Carga manual, offline y Pendientes

### Carga de Producción

![Contexto de carga admin](/manuales/capturas/admin/05-contexto.png)

La carga manual del admin usa los mismos 9 pasos: `Contexto`, `Operador`, `Equipo`, `Proceso`, `Tiempo`, `Producción`, `Consumos`, `Ubicación` y `Revisión`.

![Revisión de carga admin](/manuales/capturas/admin/13-revision.png)

En `Paso 2 - Operador`, el admin puede seleccionar el operador. En los pasos restantes confirmá equipo, proceso, horas, campos productivos dinámicos, combustible, remitos, ubicación y observaciones. Antes de `Guardar Registro`, verificá especialmente unidad, operador y equipo porque la carga impacta en reportes globales.

Si se registra combustible dentro del parte, completá `Litros de gasoil`, `KM / Horómetro al cargar`, `Remito 1` y `Lugar de Carga`. Ese parte ya genera el consumo; no lo repitas en `Carga de Combustible`.

### Borradores y trabajo offline

`Guardar borrador` conserva la carga en el dispositivo, pero no confirma un registro. La primera autenticación necesita conexión; una sesión válida puede continuar offline durante el período configurado, actualmente hasta 14 días.

![Pendientes admin](/manuales/capturas/admin/14-pendientes.png)

En `Producción > Pendientes`, el admin ve la cola local visible en ese dispositivo. Puede usar `Refrescar`, `Sincronizar`, `Reintentar`, `Ver detalle` y `Eliminar`.

<div class="warning">
La cola de Pendientes es local al dispositivo. El admin no ve automáticamente los pendientes guardados en otros teléfonos. `Eliminar` descarta la copia local y es una acción definitiva para esa cola.
</div>

### Mis Registros

`Producción > Mis Registros` permite consultar la actividad cargada por el propio usuario admin. Para revisar la actividad global usá los dashboards.

## 7. Errores frecuentes y buenas prácticas

| Situación | Qué hacer |
| --- | --- |
| No aparece un catálogo | Usá `Refrescar`, revisá la unidad y confirmá la conexión. |
| No se puede guardar Personal | Completá `Nombre` y al menos una unidad vinculada. |
| No se puede guardar un Móvil | Completá `Patente` y `Detalle`. |
| Asignación rechazada | Revisá unidad del chofer, móvil y proceso; evitá duplicados. |
| Dashboard sin datos | Ampliá el período o quitá filtros. |
| Usuario sin acceso | Revisá estado `Activo`, rol `Encargado` y `Acceso Admin`. |
| Horas o producción inválidas | Corregí valores mayores a 0 y respetá las validaciones del formulario. |
| Pendiente fallido | Abrí `Ver detalle`, revisá el error y usá `Reintentar`. |

Buenas prácticas:

- Configurá primero unidades, procesos, móviles y personal; después creá asignaciones.
- Usá `Relaciones` en unidades para revisar la configuración.
- Revisá la carga completa antes de guardar.
- No dupliques combustible ni elimines pendientes sin confirmación.
- No cambies accesos admin sin validar la necesidad operativa.
- Cerrá sesión en dispositivos compartidos.
