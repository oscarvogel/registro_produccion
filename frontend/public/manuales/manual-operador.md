<div class="cover">
  <img src="../../frontend/public/logo-forestal.png" alt="Logo Forestal">
  <h1>Manual de Usuario</h1>
  <div class="subtitle">Operador</div>
  <p class="meta">Sistema Registro Producción Forestal<br>Versión documental: Agosto 2026</p>
</div>

<div class="page-break"></div>

# Manual de Usuario - Operador

## Índice

1. Alcance y acceso
2. Sincronización y navegación móvil
3. Inicio
4. Carga de Producción en 9 pasos
5. Borradores, offline y Pendientes
6. Mis Registros y Configuración
7. Errores frecuentes y buenas prácticas

## 1. Alcance y acceso

El operador carga la producción de su usuario y de las unidades, equipos y procesos que tiene asignados. El sistema guarda el registro en el servidor cuando hay conexión y puede conservarlo en el teléfono cuando la conexión se interrumpe.

### Ingresar

![Pantalla de login móvil](/manuales/capturas/operador/01-login.png)

1. Abrí la aplicación.
2. En `DNI`, ingresá tu documento.
3. En `Contrasena`, ingresá tu contraseña.
4. Presioná `Ingresar`.

La primera validación del dispositivo necesita conexión. Si el ingreso falla, la pantalla muestra `Credenciales incorrectas`, `Sin conexión` o `No se pudo validar el ingreso` según el caso. No compartas tu contraseña ni la guardes en una captura.

## 2. Sincronización y navegación móvil

### Sincronizar al iniciar

![Sincronización inicial](/manuales/capturas/operador/02-sincronizar.png)

Presioná `Sincronizar` en el login cuando se hayan modificado usuarios, permisos o catálogos. Esperá el mensaje `Catálogos sincronizados`. Luego ingresá normalmente.

### Menú del teléfono

![Menú móvil](/manuales/capturas/operador/04-menu-movil.png)

En la barra superior, presioná el botón `Abrir navegacion`. Desde el menú podés abrir:

- `Inicio`.
- `Manuales`.
- `Combustible`.
- `Producción > Carga de Producción`.
- `Producción > Pendientes`.
- `Producción > Mis Registros`.
- `Configuración`.
- `Salir`.

Para cerrar el menú, presioná `Cerrar menu`, tocá el fondo oscuro o elegí una pantalla. La barra superior también permite `Cerrar sesión`.

## 3. Inicio

![Inicio del operador](/manuales/capturas/operador/03-inicio.png)

En `Inicio` revisá antes de cargar:

1. El estado `Servidor disponible`, `Servidor no disponible` o `Sin conexión`.
2. El nombre de usuario y el rol `Operador`.
3. La fecha seleccionada, que puede ser `Hoy`, `Ayer`, `7 días` o `Semana pasada`.
4. Los indicadores de producción, horas, registros y combustible.
5. La tarjeta `Sincronización`, donde se informa la cantidad de pendientes.

Los accesos rápidos `Ir a Carga de Producción`, `Ir a Carga de Combustible`, `Ver Pendientes` y `Abrir Mis Registros` llevan directamente a cada función.

## 4. Carga de Producción en 9 pasos

Entrá desde `Inicio` o desde `Producción > Carga de Producción`. La pantalla muestra `Paso N de 9`. En el teléfono se avanza con `Siguiente` y se vuelve con `Anterior`.

![Paso 1: contexto](/manuales/capturas/operador/05-contexto.png)

### Paso 1 - Contexto

1. En `Fecha`, elegí el día de la producción.
2. En `Unidad de Negocio`, seleccioná la unidad correspondiente.
3. Esperá que se carguen los catálogos dependientes.
4. Presioná `Siguiente`.

La unidad define los operadores, equipos, procesos, lugares de carga y referencias disponibles. Si el listado está vacío, revisá la conexión o pedí al administrador que verifique las asignaciones.

![Paso 2: operador](/manuales/capturas/operador/06-operador.png)

### Paso 2 - Operador

El campo `Operador` aparece bloqueado con el nombre del usuario que inició sesión. No se puede cambiar desde el rol operador. Confirmá que el nombre sea correcto y presioná `Siguiente`.

![Paso 3: equipo](/manuales/capturas/operador/07-equipo.png)

### Paso 3 - Equipo / Maquinaria

1. Confirmá el equipo asignado, por ejemplo `MAQUINA DEMO 01`.
2. Si necesitás cambiarlo, presioná `Cambiar`.
3. Buscá por detalle, patente o número.
4. Elegí una opción de `Asignaciones del operador` cuando aparezca.
5. Presioná `Siguiente`.

No avances con un equipo distinto del utilizado. Si no aparece, revisá la unidad y solicitá que se actualice la asignación.

![Paso 4: proceso](/manuales/capturas/operador/08-proceso.png)

### Paso 4 - Proceso / Actividad

En `Tipo de Proceso`, elegí el proceso correspondiente. La lista depende de la unidad y los campos del paso `Producción` cambian según la selección.

### Paso 5 - Control de Tiempo

![Paso 5: tiempo](/manuales/capturas/operador/09-tiempo.png)

Completá:

- `Hora Inicio`.
- `Hora Fin`.
- `Hs No Operativas`, si corresponde.
- `Motivo (lista)` y `Motivo (detalle libre)` cuando haya horas no operativas.

Las horas deben ser mayores a 0. La hora final no puede ser menor que la inicial. Además, el inicio no puede ser menor al fin del registro anterior del equipo. Si la validación falla, la pantalla muestra `Revisá las horas...`.

![Paso 6: producción dinámica](/manuales/capturas/operador/10-produccion.png)

### Paso 6 - Datos de Producción

Completá los campos que muestra el proceso. Según el catálogo pueden aparecer `TN Despachadas`, `Carros`, `Distancia Recorrida (mts)`, `M³ (metros cúbicos)`, `Plantas`, `Hectáreas (HAS)`, `Kilómetros (KM)`, `Horas a Disposición` o campos de horas de máquina.

Los valores requeridos deben ser mayores a 0. La aplicación calcula la unidad principal de producción según el primer campo productivo disponible.

![Paso 7: consumos](/manuales/capturas/operador/11-consumos.png)

### Paso 7 - Consumos

El paso agrupa `Combustible`, `Consumos` y, para el proceso correspondiente, `Sistema de Corte`.

Para registrar combustible dentro del parte:

1. Activá `¿Se cargó combustible?`.
2. Completá `Litros de gasoil`.
3. Completá `KM / Horómetro al cargar` con la lectura real.
4. Ingresá al menos `Remito 1`. `Remito 2` y `Remito 3` son opcionales.
5. Completá los aceites que correspondan.

<div class="warning">
El combustible cargado dentro del parte descuenta stock. No repitas ese abastecimiento en `Carga de Combustible`, porque duplicarías el consumo.
</div>

Si el proceso es `PROCESO`, también se solicitan `Espada`, `Puntera`, `Cadena`, `Piñón` y `Cantidad de Cadenas`.

![Paso 8: ubicación](/manuales/capturas/operador/12-ubicacion.png)

### Paso 8 - Ubicación y Referencia

Completá los campos que el tipo de proceso exige:

- `Lugar de Carga`, siempre que el parte registre combustible.
- `Acta`, si el proceso la requiere.
- `Predio`, si el proceso lo requiere.
- `Rodal`, desde la lista vinculada, o `Rodal` manual cuando no exista una opción.
- `Observaciones`, para notas adicionales.

Si el tipo de trabajo no requiere Acta, Predio ni Rodal, la pantalla lo informa. Si falta una referencia obligatoria, aparece `Completá Acta, Predio, Rodal o Lugar de Carga para este tipo de trabajo`.

![Paso 9: revisión](/manuales/capturas/operador/13-revision.png)

### Paso 9 - Revisión y Confirmación

Antes de guardar, revisá fecha, unidad, operador, equipo, proceso, horario, producción, horas no operativas y ubicación. Si todo es correcto, presioná `Guardar Registro`.

El resultado esperado es el mensaje `Registro guardado`. Si no hay conexión, el parte queda en el teléfono y se informa que debe revisarse en `Pendientes`.

## 5. Borradores, offline y Pendientes

### Guardar borrador

En cualquier paso disponible, presioná `Guardar borrador` para conservar la carga en el dispositivo. El mensaje esperado es `Borrador guardado`. El borrador no es un registro confirmado: volvé a la carga, revisalo y completá el guardado final.

### Trabajo sin conexión

![Pendientes locales](/manuales/capturas/operador/14-pendientes.png)

La primera entrada en un teléfono requiere conexión. Después, una sesión válida puede habilitar el ingreso offline durante el período configurado, actualmente hasta 14 días. Una carga sin conexión queda en la cola local y muestra `Guardado solo en este teléfono`.

En `Producción > Pendientes` podés:

1. Revisar `Pendientes locales` y `Fallidos locales`.
2. Presionar `Refrescar` para actualizar el estado.
3. Presionar `Sincronizar` cuando el servidor esté disponible.
4. Usar `Reintentar` en un registro puntual.
5. Usar `Ver detalle` para revisar el payload guardado.
6. Usar `Eliminar` sólo si confirmás que el registro no debe enviarse.

<div class="warning">
`Eliminar` descarta el registro de la cola local del dispositivo. La acción es definitiva para esa copia y no reemplaza una corrección del registro en el servidor.
</div>

## 6. Mis Registros y Configuración

![Mis registros](/manuales/capturas/operador/15-mis-registros.png)

En `Producción > Mis Registros` consultá las cargas realizadas por tu usuario, sus totales, horas y consumos. Usá el período para acotar la consulta.

En `Configuración` podés instalar la PWA cuando el navegador lo ofrezca y cerrar sesión. En un teléfono compartido, usá `Salir` al finalizar.

## 7. Errores frecuentes y buenas prácticas

| Situación | Qué hacer |
| --- | --- |
| `Credenciales incorrectas` | Revisá DNI y contraseña. No repitas contraseñas en capturas o mensajes. |
| `Sin conexión` en el login | Conectá el teléfono para validar la primera sesión o revalidar una sesión vencida. |
| No aparece la unidad | Usá `Sincronizar` y verificá que el usuario tenga una unidad activa. |
| No aparece el equipo | Confirmá la unidad y la asignación del equipo al operador. |
| `Revisá las horas` | Usá valores mayores a 0 y un fin mayor o igual al inicio; respetá el fin anterior del equipo. |
| Producción inválida | Completá los campos dinámicos con valores mayores a 0. |
| Falta Acta, Predio, Rodal o Lugar de Carga | Completá la referencia exigida por el proceso. |
| Pendiente fallido | Abrí `Ver detalle`, revisá el error y usá `Reintentar`. |

Buenas prácticas:

- Confirmá unidad, equipo y proceso antes de completar producción.
- No cargues dos veces el mismo abastecimiento de combustible.
- Revisá el resumen final antes de guardar.
- Sincronizá los pendientes cuando recuperes conexión.
- Cerrá sesión si el dispositivo es compartido.
