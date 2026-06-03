<div class="cover">
  <img src="../../frontend/public/logo-forestal.png" alt="Logo Forestal">
  <h1>Manual de Usuario</h1>
  <div class="subtitle">Operador</div>
  <p class="meta">Sistema Registro Produccion Forestal<br>Version documental: Junio 2026</p>
</div>

<div class="page-break"></div>

# Manual de Usuario - Operador

## Indice

1. Alcance del rol
2. Acceso al sistema
3. Navegacion principal
4. Carga de Produccion
5. Trabajo sin conexion y sincronizacion
6. Mis Registros
7. Configuracion, instalacion y salida
8. Errores frecuentes y buenas practicas

## 1. Alcance del rol

El operador usa el sistema para registrar su produccion diaria, revisar sus cargas personales y controlar los registros que quedaron pendientes de sincronizacion.

Como operador podes:

- Ingresar con DNI y contrasena.
- Sincronizar datos de acceso desde la pantalla de login.
- Cargar registros de produccion propios.
- Guardar borradores locales durante una carga.
- Trabajar sin conexion; el sistema guarda la carga localmente.
- Ver y reintentar registros pendientes generados por tu usuario.
- Consultar `Mis Registros` con filtros por periodo.
- Instalar la aplicacion como PWA cuando el navegador lo permita.
- Cerrar sesion.

No corresponde al rol operador:

- Ver el dashboard operativo general.
- Seleccionar otro operador para una carga.
- Administrar personal, moviles, unidades, procesos o accesos.

## 2. Acceso al sistema

1. Abrir la aplicacion.
2. En la pantalla `Acceso operativo`, ingresar el `DNI`.
3. Ingresar la `Contrasena`.
4. Presionar `Ingresar`.

Si el sistema muestra `DNI o contrasena incorrectos`, revisar los datos ingresados. Si muestra un error de conexion, verificar la red e intentar nuevamente.

### Sincronizar desde el login

La pantalla de ingreso incluye el boton `Sincronizar`. Usalo cuando se hayan actualizado usuarios o permisos y necesites traer la informacion vigente antes de iniciar sesion.

Al finalizar correctamente, el sistema informa el resultado y la cantidad de personal activo sincronizado.

## 3. Navegacion principal

Una vez iniciada la sesion, la aplicacion muestra el menu lateral o el menu movil segun el dispositivo.

Pantallas disponibles para operador:

| Pantalla | Uso principal |
| --- | --- |
| `Inicio` | Resumen personal del dia, estado de conexion, ultimos datos y accesos rapidos. |
| `Carga de Produccion` | Alta guiada de una carga productiva. |
| `Pendientes` | Cola local de registros sin enviar o con error. |
| `Mis Registros` | Historial y totales personales por periodo. |
| `Configuracion` | Instalacion de la app y cierre de sesion. |

En la parte superior puede aparecer una franja `Sin conexion`. Cuando aparece, las nuevas cargas se guardan localmente y se sincronizan al reconectar.

## 4. Carga de Produccion

Entrar desde `Inicio` con `Carga de Produccion` o desde el menu `Produccion > Carga de Produccion`.

El formulario esta organizado en 9 pasos. En cada paso, completar los datos solicitados y avanzar con `Siguiente`. En escritorio se ve el panel de progreso; en movil se muestra el paso actual y una barra de avance.

### Paso 1: Contexto

Completar:

- `Fecha`: dia correspondiente a la produccion. Si estas cargando produccion atrasada, modificar la fecha.
- `Unidad de Negocio`: unidad para la que se registra la carga.

Si el usuario tiene una sola unidad disponible o una preferencia guardada, el sistema puede precargarla.

### Paso 2: Operador

Para el rol operador, el campo `Operador` aparece bloqueado con el nombre del usuario logueado. No se debe cambiar manualmente.

### Paso 3: Equipo / Maquinaria

El sistema intenta autocompletar la maquinaria por asignaciones del operador.

Opciones posibles:

- Elegir una opcion de `Asignaciones del operador`.
- Buscar una maquina por numero, marca, detalle o patente.
- Usar `Cambiar` si ya habia una maquina seleccionada y corresponde reemplazarla.

### Paso 4: Proceso / Actividad

Seleccionar el `Tipo de Proceso`. Los campos de produccion cambian segun el proceso seleccionado.

Si el operador tiene un proceso asignado, el sistema puede precargarlo.

### Paso 5: Control de Tiempo

Completar:

- `Hora Inicio`.
- `Hora Fin`.
- `Hs No Operativas`, si aplica.
- `Motivo (lista)` y `Motivo (detalle libre)`, si hubo tiempo no operativo.

La hora final no puede ser menor que la inicial. Si existe un registro anterior para la maquina, la hora de inicio no puede ser menor al fin anterior.

### Paso 6: Datos de Produccion

Completar los campos que aparecen para el tipo de proceso seleccionado. Algunos ejemplos:

- `TN Despachadas`.
- `Carros`.
- `Distancia Recorrida (mts)`.
- `M3`.
- `Plantas`.
- `Hectareas`.
- `KM`.
- `Horas a disposicion`.

Los campos productivos requeridos deben cargarse con valores mayores a 0. Para procesos de corte pueden aparecer campos como `16 Pies`, `14 Pies`, `12 Pies`, `10 Pies` y `Pulpable`.

### Paso 7: Consumos

Usar este paso para registrar combustible y consumos asociados cuando corresponda.

Campos habituales:

- `Combustible`.
- `Aceite cadena`.
- `Aceite hidraulico`.
- `Aceite motor`.
- `Aceite transmision`.
- `Aceite embrague`.
- Datos del sistema de corte, cuando el proceso lo solicita.

Si no se cargo combustible, dejar el control desactivado o en 0.

### Paso 8: Ubicacion y Referencia

Completar:

- `Lugar de Carga`, si esta disponible para la unidad.
- `Acta`.
- `Predio`.
- `Rodal` desde la lista o `Rodal manual`.

Para guardar, la ubicacion debe estar completa cuando el sistema la solicita. El `Acta` es obligatoria y no debe quedar vacia ni en 0.

Tambien puede completarse `Observaciones` con informacion adicional.

### Paso 9: Revision y Confirmacion

Revisar el resumen antes de guardar:

- Fecha.
- Unidad de negocio.
- Operador.
- Equipo.
- Proceso.
- Horario.
- Produccion.
- Ubicacion.

Si algun dato no corresponde, volver al paso anterior y corregirlo. Cuando este correcto, guardar el registro.

### Guardar borrador

El boton `Guardar borrador` guarda la carga en este dispositivo. Usalo si necesitas interrumpir la carga antes de finalizarla.

El borrador no reemplaza el guardado final del registro. Para registrar produccion, siempre completar la revision y guardar.

## 5. Trabajo sin conexion y sincronizacion

La aplicacion soporta trabajo offline.

Cuando no hay conexion:

- Aparece el aviso `Sin conexion`.
- Las cargas se guardan localmente.
- El sistema indica que el registro se enviara automaticamente al recuperar la conexion.

Cuando vuelve la conexion:

- La aplicacion intenta sincronizar automaticamente.
- Tambien se puede entrar en `Pendientes` y usar `Sincronizar` o `Reintentar`.

### Pantalla Registros Pendientes

En `Pendientes` se ve el estado de la cola local.

Acciones disponibles:

- `Refrescar`: vuelve a leer la cola local.
- `Sincronizar`: intenta enviar todos los registros pendientes visibles.
- `Reintentar`: intenta enviar un registro puntual.
- `Ver detalle`: muestra la informacion guardada localmente.
- `Eliminar`: descarta un registro local.

<div class="warning">
Eliminar un pendiente borra la carga local. Usar esta accion solo si el registro no debe enviarse o fue cargado nuevamente por otro medio.
</div>

## 6. Mis Registros

Entrar desde `Produccion > Mis Registros`.

Esta pantalla muestra el historial personal y totales del periodo seleccionado.

Filtros disponibles:

- `Hoy`.
- `Esta semana`.
- `Este mes`.
- `Desde`.
- `Hasta`.

Indicadores visibles:

- Cantidad de registros.
- Horas trabajadas.
- Combustible.
- Combustible por hora, si hay datos.
- Totales productivos segun el tipo de carga: toneladas, metros cubicos, hectareas, carros, plantas, kilometros.

Cada registro muestra proceso, fecha, equipo y metricas cargadas.

## 7. Configuracion, instalacion y salida

En `Configuracion` se encuentran:

- `Instalar App`: disponible cuando el navegador permite instalar la PWA.
- `Cerrar sesion`: finaliza la sesion actual y vuelve al login.

Tambien se puede cerrar sesion desde el menu lateral o desde el encabezado movil.

## 8. Errores frecuentes y buenas practicas

| Situacion | Que hacer |
| --- | --- |
| No puedo ingresar | Revisar DNI y contrasena. Si hubo cambios recientes, usar `Sincronizar` en login. |
| Estoy sin conexion | Cargar normalmente; el registro queda local y se envia al reconectar. |
| Hora invalida | Verificar que inicio y fin sean mayores a 0 y que fin no sea menor que inicio. |
| Produccion invalida | Completar los campos requeridos con valores mayores a 0. |
| Ubicacion incompleta | Completar Acta, Predio y Rodal cuando sean solicitados. |
| Hay pendientes fallidos | Entrar en `Pendientes`, revisar `Ver detalle` y usar `Reintentar`. |

Buenas practicas:

- Confirmar unidad, equipo y proceso antes de cargar produccion.
- Cargar las horas en formato numerico consistente, por ejemplo `1200` y `1850`.
- Revisar el paso final antes de guardar.
- No eliminar pendientes salvo que se confirme que no deben enviarse.
- Cerrar sesion al terminar si el dispositivo es compartido.
