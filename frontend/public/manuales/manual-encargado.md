<div class="cover">
  <img src="../../frontend/public/logo-forestal.png" alt="Logo Forestal">
  <h1>Manual de Usuario</h1>
  <div class="subtitle">Encargado</div>
  <p class="meta">Sistema Registro Producción Forestal<br>Versión documental: Agosto 2026</p>
</div>

<div class="page-break"></div>

## Índice

1. [Alcance y acceso](#1-alcance-y-acceso)
2. [Inicio y navegación móvil](#2-inicio-y-navegacion-movil)
3. [Carga de Producción por operador](#3-carga-de-produccion-por-operador)
4. [Operación](#4-operacion)
5. [Detalle de registros y verificación de la evidencia](#5-detalle-de-registros-y-verificacion-de-la-evidencia)
6. [Pendientes por unidad y trabajo offline](#6-pendientes-por-unidad-y-trabajo-offline)
7. [Configuración y buenas prácticas](#7-configuracion-y-buenas-practicas)

## 1. Alcance y acceso

El encargado registra producción para sus unidades asignadas y puede elegir el operador de cada carga. También consulta `Operación` con filtros operativos y revisa la evidencia fotográfica de los registros para verificarla o rechazarla. No administra catálogos, personal, accesos admin ni asignaciones.

![Login del encargado](/manuales/capturas/encargado/01-login.png)

Para ingresar:

1. Abrí la aplicación.
2. Completá `DNI` y `Contraseña`.
3. Presioná `Actualizar datos para uso offline` si hubo cambios de permisos o catálogos.
4. Presioná `Ingresar`.

La primera entrada al dispositivo necesita conexión. Los mensajes de error visibles son `Credenciales incorrectas`, `Sin conexión` y `No se pudo validar el ingreso`.

## 2. Inicio y navegación móvil

![Inicio del encargado](/manuales/capturas/encargado/03-inicio.png)

En `Inicio` revisá estado de servidor, fecha, indicadores de producción, horas, registros, combustible y pendientes. Los accesos principales son `Ir a Carga de Producción`, `Ir a Carga de Combustible`, `Ver Pendientes` y `Abrir Operación`.

![Menú móvil del encargado](/manuales/capturas/encargado/04-menu-movil.png)

Presioná `Abrir navegación` para abrir `Inicio`, `Manuales`, `Combustible`, `Producción`, `Pendientes`, `Operación`, `Configuración` y `Salir`. Tocá `Cerrar menú` o el fondo para cerrar el panel.

## 3. Carga de Producción por operador

El formulario muestra 9 pasos. En el teléfono se avanza con `Siguiente`, se vuelve con `Anterior` y se puede conservar un `Guardar borrador` en el dispositivo.

Cuando el tipo de proceso que elegiste pide foto de respaldo, el formulario suma un paso, `Evidencia`, entre `Producción` y `Consumos`, y la pantalla muestra `Paso N de 10`. El paso aparece sólo en los tipos de proceso que lo piden.

![Paso 1: contexto](/manuales/capturas/encargado/05-contexto.png)

### Paso 1 - Contexto

Elegí `Fecha` y `Unidad de Negocio`. La unidad limita los operadores, equipos, procesos y lugares de carga disponibles. Esperá que finalice la carga de catálogos antes de continuar.

![Paso 2: seleccionar operador](/manuales/capturas/encargado/06-operador.png)

### Paso 2 - Operador

1. En `Seleccionar Operador`, buscá por nombre.
2. Elegí el operador que realizó el trabajo.
3. Confirmá que la unidad elegida sea la correcta.

Al elegir un operador, la aplicación consulta sus asignaciones y puede completar equipo y proceso sugeridos. La selección es importante porque el registro queda asociado al operador elegido.

![Paso 3: equipo](/manuales/capturas/encargado/07-equipo.png)

### Paso 3 - Equipo / Maquinaria

Confirmá la asignación sugerida. Si hace falta, presioná `Cambiar` y buscá la máquina por detalle, patente o número. No elijas una máquina que no corresponda a la unidad o al trabajo realizado.

![Paso 4: proceso](/manuales/capturas/encargado/08-proceso.png)

### Paso 4 - Proceso / Actividad

En `Tipo de Proceso`, seleccioná el proceso disponible para la unidad. Esta selección determina los campos productivos y los requisitos de ubicación.

![Paso 5: tiempo](/manuales/capturas/encargado/09-tiempo.png)

### Paso 5 - Control de Tiempo

Completá `Horómetro inicial`, `Horómetro final`, `Hs No Operativas`, `Motivo (lista)` y `Motivo (detalle libre)` cuando corresponda. Inicio y fin deben ser mayores a 0; el fin no puede ser menor que el inicio; y el inicio no puede ser menor al último fin registrado para el equipo.

![Paso 6: producción](/manuales/capturas/encargado/10-produccion.png)

### Paso 6 - Datos de Producción

Completá sólo los campos que muestre el proceso: `TN Despachadas`, `Carros`, `Distancia Recorrida (mts)`, `M³ (metros cúbicos)`, `Plantas`, `Hectáreas (HAS)`, `Kilómetros (KM)`, `Horas a Disposición` u horas de máquina. Los valores requeridos deben ser mayores a 0.

### Paso 7 - Evidencia Fotográfica

Este paso aparece sólo cuando el tipo de proceso pide foto de respaldo. La pantalla se titula `Evidencia Fotográfica` y avisa: **"Este tipo de proceso pide foto de respaldo. Tomala ahora: se sube al guardar el registro y después la revisa el encargado."**

Qué se pide depende del tipo de proceso:

- `Foto de la pantalla del procesador`: **"Mostrá la pantalla del procesador (plantas y/o m³)."**
- `Foto del horómetro`: **"Fotografiá el horómetro con la lectura final."** El texto de ayuda recuerda la lectura que hay que documentar, por ejemplo `Documentá la lectura final: 1850.`

Los dos campos aparecen con el distintivo `Obligatoria` hasta que tienen foto; después pasa a `Lista`. El botón `Tomar foto` abre la cámara del teléfono. Con la foto puesta se ve una miniatura y aparecen `Rehacer foto` y `Quitar`.

**La casilla "En esa misma pantalla se ve el horómetro".** Si la foto del procesador ya muestra el horómetro, marcá esta casilla: con esa sola foto alcanza y no hace falta sacar otra. Al marcarla desaparece el campo `Foto del horómetro` y la foto de la pantalla cubre los dos casos.

<div class="warning">
El paso no deja avanzar sin la foto. Si aparece el error `Falta la foto de evidencia. No se puede guardar el registro sin ella.`, falta la foto del procesador: tomala antes de seguir.
</div>

La foto se sube junto con el registro, en el paso `Revisión`.

![Paso 8: consumos](/manuales/capturas/encargado/11-consumos.png)

### Paso 8 - Consumos

El paso incluye `Combustible`, `Consumos` y, si el proceso lo solicita, `Sistema de Corte`.

1. Activá `¿Se cargó combustible?` cuando corresponda.
2. Completá `Litros de gasoil`, `KM / Horómetro al cargar` y `Remito 1`.
3. Completá aceites y datos de corte si aplican.

<div class="warning">
El combustible incluido en el parte descuenta stock. No vuelvas a registrarlo en `Carga de Combustible`.
</div>

![Paso 9: ubicación](/manuales/capturas/encargado/12-ubicacion.png)

### Paso 9 - Ubicación y Referencia

Completá `Lugar de Carga` cuando haya combustible. `Acta`, `Predio` y `Rodal` aparecen y se vuelven obligatorios según los requisitos del proceso. Agregá `Observaciones` para aclaraciones.

![Paso 10: revisión](/manuales/capturas/encargado/13-revision.png)

### Paso 10 - Revisión y Confirmación

Revisá fecha, unidad, operador, equipo, proceso, horario, producción, consumos, evidencia fotográfica y ubicación. Si la carga es correcta, presioná `Guardar Registro`. Si falta un dato, volvé con `Anterior` y corregilo antes de guardar.

## 4. Operación

![Operación](/manuales/capturas/encargado/15-dashboard-operativo.png)

Entrá desde `Operación` o desde el acceso rápido. La pantalla permite analizar sólo las unidades que tiene asignadas el encargado.

### Filtros

1. Elegí `Unidad de Negocio`.
2. Opcionalmente filtrá por `Tipo de Proceso`.
3. Opcionalmente elegí `Máquina / Equipo`.
4. Definí `Desde` y `Hasta`.
5. En el teléfono, presioná `Filtros` para mostrar u ocultar los campos.
6. Usá `Limpiar` para quitar filtros adicionales.

La vista de Operación muestra la métrica principal, KPIs secundarios, `Evolución diaria`, evolución de combustible y `Ranking de Máquinas`. Si no hay resultados, ampliá el período o quitá filtros. Si aparece `Sin unidades disponibles`, solicitá la revisión de tus permisos.

## 5. Detalle de registros y verificación de la evidencia

Desde `Operación` se abre `Detalle de registros`: el listado de los registros individuales, con la foto que cargó el operador.

### El filtro de evidencia

El listado tiene un filtro del estado de la evidencia:

| Opción | Qué muestra |
| --- | --- |
| `Todas` | Todos los registros (opción por defecto). |
| `Esperando verificación` | Sólo los registros con fotos sin revisar. |
| `Con foto rechazada` | Sólo los registros con alguna foto rechazada. |
| `Sin evidencia` | Sólo los registros que no tienen ninguna foto. |

El filtro se aplica en el servidor, no en el navegador: los que quedan son los de todas las páginas, no sólo los de la página cargada, y el total de la paginación sigue cuadrando.

### Las marcas del listado

Cada registro marca el estado de su evidencia en la columna `Operación`:

- `Sin verificar` (ámbar): tiene fotos esperando revisión.
- `Observado` (rojo): alguna foto fue rechazada.

No se agregó una columna nueva: el listado ya tiene muchas y una más lo desbordaría en las notebooks de la planta.

### El aviso por WhatsApp

Cuando un operador carga un registro con evidencia, el sistema manda un **WhatsApp al encargado de la unidad**. El mensaje dice qué registro es, que hay fotos esperando y que hay que validarlas.

Ese aviso es una cortesía: si el WhatsApp no sale (no hay número cargado, el servicio está caído o la aplicación quedó sin conexión), **el registro se guarda igual** y la evidencia queda esperando en el filtro `Esperando verificación`.

<div class="warning">
El aviso no reemplaza la revisión: hay que entrar al `Detalle de registros` y verificar las fotos. El WhatsApp es para enterarte rápido, no para validar.
</div>

### La sección Evidencia Fotográfica del detalle

Al abrir un registro que tiene fotos, el detalle incluye una sección `Evidencia Fotográfica` con una ficha por foto:

- La **foto**.
- El **rol** que cubre: `Foto de la pantalla del procesador` o `Foto del horómetro`.
- El **estado**: `Pendiente de verificación`, `Verificada`, `Rechazada` o `Reemplazada`.
- La **declaración del operador**, cuando corresponde: **"El operador declaró que el horómetro se ve en esta pantalla. Revisá la foto: si el horómetro no se ve, rechazala con el motivo."**
- Quién la verificó y cuándo, una vez revisada.
- El `Motivo: ...`, si fue rechazada.

Ese aviso en ámbar es lo que hace útil la foto: el operador declaró que el horómetro se ve en esa pantalla, así que hay que contrastarlo con la imagen.

### Verificar

Con la foto `Pendiente de verificación`, usá el botón `Verificar`. La foto queda `Verificada` y se guarda quién la verificó y la fecha.

`Verificar` significa que la foto sirve de respaldo: la pantalla del procesador se ve y, si el operador declaró que el horómetro se ve en ella, efectivamente se ve.

### Rechazar

Con el botón `Rechazar` se pide el motivo. La foto queda `Rechazada` con ese texto a la vista, que es lo que después lee el operador para saber qué corregir.

El motivo es **obligatorio**: sin él, el sistema pide `Contá el motivo del rechazo (por lo menos 5 letras)`. Un motivo útil es el que dice qué corregir, por ejemplo `el horómetro no se ve en la pantalla`.

<div class="warning">
Rechazar no borra la foto ni el registro: deja la foto en estado `Rechazada` con el motivo. Si el operador vuelve a subir una foto de corrección, esa foto nueva queda `Pendiente de verificación` y vuelve a avisar por WhatsApp.
</div>

Los botones `Verificar` y `Rechazar` sólo aparecen para el rol `Encargado` y para `Admin`. El operador ve la foto y el estado, pero no puede cambiarlos.

## 6. Pendientes por unidad y trabajo offline

![Pendientes del encargado](/manuales/capturas/encargado/14-pendientes.png)

En `Producción > Pendientes` el encargado ve los registros locales asociados a sus unidades asignadas. Las tarjetas informan `Pendientes locales`, `Fallidos locales`, pendientes y fallidos de unidad.

Acciones:

- `Refrescar`: vuelve a consultar el estado.
- `Sincronizar`: intenta enviar todos los pendientes visibles cuando el servidor está disponible.
- `Reintentar`: reenvía un registro.
- `Ver detalle`: muestra el payload local.
- `Eliminar`: descarta la copia local.

<div class="warning">
La cola es local al dispositivo. El encargado no ve automáticamente los pendientes que existen en otros teléfonos. No uses `Eliminar` sin confirmar que el registro no debe enviarse.
</div>

Sin conexión, una sesión previamente validada puede continuar dentro del período offline configurado, actualmente hasta 14 días. Las nuevas cargas quedan en la cola local y se sincronizan al recuperar conexión.

## 7. Configuración y buenas prácticas

En `Configuración` podés usar `Instalar App` si el navegador ofrece la instalación PWA y luego `Cerrar sesión`. En un dispositivo compartido, cerrá sesión al finalizar.

| Situación | Qué hacer |
| --- | --- |
| No aparece el operador | Revisá la unidad seleccionada y presioná `Sincronizar` en el próximo ingreso. |
| No aparece la máquina | Confirmá la unidad y las asignaciones del operador. |
| No aparecen procesos | Verificá que existan procesos habilitados para la unidad. |
| Horas inválidas | Usá valores mayores a 0 y respetá la secuencia del último registro del equipo. |
| Falta la foto de evidencia | El paso `Evidencia` no deja avanzar: tomá la foto de la pantalla del procesador. Si esa foto ya muestra el horómetro, marcá la casilla y no hace falta la segunda. |
| No me llega el WhatsApp del aviso | El aviso es una cortesía: el registro se guardó igual. Revisá el filtro `Esperando verificación` del `Detalle de registros`, que es la fuente de verdad. |
| El rechazo me pide el motivo | Es obligatorio y tiene que decir qué corregir (por lo menos 5 letras). |
| Un registro sale `Observado` | Tiene una foto rechazada: abrí el detalle y leé `Motivo: ...` para saber qué corregir. |
| Falta ubicación | Completá los campos que exige el proceso y el `Lugar de Carga` si hay combustible. |
| Operación sin datos | Ampliá fechas o quitá filtros. |
| Pendiente fallido | Abrí `Ver detalle`, revisá el error y usá `Reintentar`. |

Buenas prácticas:

- Confirmá la unidad antes de seleccionar operador y equipo.
- Revisá el resumen final porque la carga puede afectar reportes globales.
- Revisá las fotos pendientes seguido: el filtro `Esperando verificación` es la cola de trabajo del encargado.
- Rechazá con un motivo concreto: es lo único que le sirve al operador para saber qué corregir.
- No dupliques consumos de combustible.
- No elimines pendientes sin confirmación.
