<div class="cover">
  <img src="../../frontend/public/logo-forestal.png" alt="Logo Forestal">
  <h1>Manual de Usuario</h1>
  <div class="subtitle">Encargado</div>
  <p class="meta">Sistema Registro Producción Forestal<br>Versión documental: Agosto 2026</p>
</div>

<div class="page-break"></div>

# Manual de Usuario - Encargado

## Índice

1. Alcance y acceso
2. Inicio y navegación móvil
3. Carga de Producción por operador
4. Dashboard Operativo
5. Pendientes por unidad y trabajo offline
6. Configuración y buenas prácticas

## 1. Alcance y acceso

El encargado registra producción para sus unidades asignadas y puede elegir el operador de cada carga. También consulta el `Dashboard de Producción` con filtros operativos. No administra catálogos, personal, accesos admin ni asignaciones.

![Login del encargado](/manuales/capturas/encargado/01-login.png)

Para ingresar:

1. Abrí la aplicación.
2. Completá `DNI` y `Contrasena`.
3. Presioná `Sincronizar` si hubo cambios de permisos o catálogos.
4. Presioná `Ingresar`.

La primera entrada al dispositivo necesita conexión. Los mensajes de error visibles son `Credenciales incorrectas`, `Sin conexión` y `No se pudo validar el ingreso`.

## 2. Inicio y navegación móvil

![Inicio del encargado](/manuales/capturas/encargado/03-inicio.png)

En `Inicio` revisá estado de servidor, fecha, indicadores de producción, horas, registros, combustible y pendientes. Los accesos principales son `Ir a Carga de Producción`, `Ir a Carga de Combustible`, `Ver Pendientes` y `Abrir Dashboard Operativo`.

![Menú móvil del encargado](/manuales/capturas/encargado/04-menu-movil.png)

Presioná `Abrir navegacion` para abrir `Inicio`, `Manuales`, `Combustible`, `Producción`, `Pendientes`, `Dashboard Operativo`, `Configuración` y `Salir`. Tocá `Cerrar menu` o el fondo para cerrar el panel.

## 3. Carga de Producción por operador

El formulario muestra 9 pasos. En el teléfono se avanza con `Siguiente`, se vuelve con `Anterior` y se puede conservar un `Guardar borrador` en el dispositivo.

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

Completá `Hora Inicio`, `Hora Fin`, `Hs No Operativas`, `Motivo (lista)` y `Motivo (detalle libre)` cuando corresponda. Inicio y fin deben ser mayores a 0; el fin no puede ser menor que el inicio; y el inicio no puede ser menor al último fin registrado para el equipo.

![Paso 6: producción](/manuales/capturas/encargado/10-produccion.png)

### Paso 6 - Datos de Producción

Completá sólo los campos que muestre el proceso: `TN Despachadas`, `Carros`, `Distancia Recorrida (mts)`, `M³ (metros cúbicos)`, `Plantas`, `Hectáreas (HAS)`, `Kilómetros (KM)`, `Horas a Disposición` u horas de máquina. Los valores requeridos deben ser mayores a 0.

![Paso 7: consumos](/manuales/capturas/encargado/11-consumos.png)

### Paso 7 - Consumos

El paso incluye `Combustible`, `Consumos` y, si el proceso lo solicita, `Sistema de Corte`.

1. Activá `¿Se cargó combustible?` cuando corresponda.
2. Completá `Litros de gasoil`, `KM / Horómetro al cargar` y `Remito 1`.
3. Completá aceites y datos de corte si aplican.

<div class="warning">
El combustible incluido en el parte descuenta stock. No vuelvas a registrarlo en `Carga de Combustible`.
</div>

![Paso 8: ubicación](/manuales/capturas/encargado/12-ubicacion.png)

### Paso 8 - Ubicación y Referencia

Completá `Lugar de Carga` cuando haya combustible. `Acta`, `Predio` y `Rodal` aparecen y se vuelven obligatorios según los requisitos del proceso. Agregá `Observaciones` para aclaraciones.

![Paso 9: revisión](/manuales/capturas/encargado/13-revision.png)

### Paso 9 - Revisión y Confirmación

Revisá fecha, unidad, operador, equipo, proceso, horario, producción, consumos y ubicación. Si la carga es correcta, presioná `Guardar Registro`. Si falta un dato, volvé con `Anterior` y corregilo antes de guardar.

## 4. Dashboard Operativo

![Dashboard operativo](/manuales/capturas/encargado/15-dashboard-operativo.png)

Entrá desde `Operación > Dashboard Operativo` o desde el acceso rápido. La pantalla permite analizar sólo las unidades que tiene asignadas el encargado.

### Filtros

1. Elegí `Unidad de Negocio`.
2. Opcionalmente filtrá por `Tipo de Proceso`.
3. Opcionalmente elegí `Máquina / Equipo`.
4. Definí `Desde` y `Hasta`.
5. En el teléfono, presioná `Filtros` para mostrar u ocultar los campos.
6. Usá `Limpiar` para quitar filtros adicionales.

El dashboard muestra la métrica principal, KPIs secundarios, `Evolución diaria`, evolución de combustible y `Ranking de Máquinas`. Si no hay resultados, ampliá el período o quitá filtros. Si aparece `Sin unidades disponibles`, solicitá la revisión de tus permisos.

## 5. Pendientes por unidad y trabajo offline

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

## 6. Configuración y buenas prácticas

En `Configuración` podés usar `Instalar App` si el navegador ofrece la instalación PWA y luego `Cerrar sesión`. En un dispositivo compartido, cerrá sesión al finalizar.

| Situación | Qué hacer |
| --- | --- |
| No aparece el operador | Revisá la unidad seleccionada y presioná `Sincronizar` en el próximo ingreso. |
| No aparece la máquina | Confirmá la unidad y las asignaciones del operador. |
| No aparecen procesos | Verificá que existan procesos habilitados para la unidad. |
| Horas inválidas | Usá valores mayores a 0 y respetá la secuencia del último registro del equipo. |
| Falta ubicación | Completá los campos que exige el proceso y el `Lugar de Carga` si hay combustible. |
| Dashboard sin datos | Ampliá fechas o quitá filtros. |
| Pendiente fallido | Abrí `Ver detalle`, revisá el error y usá `Reintentar`. |

Buenas prácticas:

- Confirmá la unidad antes de seleccionar operador y equipo.
- Revisá el resumen final porque la carga puede afectar reportes globales.
- No dupliques consumos de combustible.
- No elimines pendientes sin confirmación.
