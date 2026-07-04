## Contexto

Cuando el operador intenta hacer login sin red, la pantalla muestra el mismo rojo de "Error del servidor" / "Error de conexión" sin distinguir si el problema es conectividad o credenciales. Eso confunde al operador y no le permite decidir qué hacer (volver a intentar vs esperar señal).

Adicionalmente, en errores 5xx el interceptor global de `api.js` (`frontend/src/services/api.js:46-52`) muestra `error.response?.data?.detail`, que puede incluir trazas de SQL o de pymysql (relacionado con issue #24).

## Comportamiento esperado

El operador debe ver:

- **Sin red** (`navigator.onLine === false` o error sin `response`): "Estás sin conexión. Si ya iniciaste sesión en este dispositivo, podés seguir trabajando. Si no, esperá a tener señal."
- **Credenciales incorrectas** (`status === 401`): "DNI o contraseña incorrectos."
- **Backend caído pero con red** (`status >= 500`): mensaje genérico y un botón "Reintentar" / "Estado del servidor".
- **Backend OK pero otro error** (`status === 4xx` distinto de 401): el mensaje del backend si es legible, sino mensaje genérico.

## Tareas

1. En `frontend/src/views/LoginView.vue`, clasificar el error antes de mostrarlo.
2. En `frontend/src/services/api.js`, NO usar `data.detail` para 5xx en login (`/api/auth/login`); usar mensaje genérico.
3. Agregar un indicador visual "Sin conexión" cerca del formulario cuando aplique.
4. Agregar test unitario para los cuatro casos.

## Criterios de aceptación

- Login sin red muestra mensaje claro de "sin conexión" sin texto rojo alarmante.
- Login con credenciales malas sigue mostrando "DNI o contraseña incorrectos".
- Login con backend 5xx no muestra SQL ni stack traces (resuelve también parte del #24).

## Prioridad

P0 — bloqueante para uso en campo.
