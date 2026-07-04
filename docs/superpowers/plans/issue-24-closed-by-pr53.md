## Contexto

La issue #24 pedia que el login no muestre errores internos de MySQL (SQL, stack traces, pymysql, etc.) al usuario final, y que el detalle tecnico del backend solo quede en logs del server.

## Estado al cierre

Implementado y deployado en produccion por:

- **PR #53** (`fix(ui): clasificar errores de login (sin red vs 401 vs 5xx)`, https://github.com/oscarvogel/registro_produccion/pull/53) introdujo:
  - `frontend/src/stores/auth.js` -> `classifyLoginError()` que mapea errores axios a mensajes amigables. Rechaza eco de `data.detail` si luce tecnico (`pymysql`, `sqlalchemy`, `password_hash`, `INSERT`, etc.) o si mide mas de 120 caracteres.
  - 3 constantes publicas:
    - `LOGIN_ERROR_NO_CONNECTION` = "Estas sin conexion. Necesitamos senal para validar el ingreso."
    - `LOGIN_ERROR_BAD_CREDENTIALS` = "DNI o contrasena incorrectos"
    - `LOGIN_ERROR_SERVER` = "No se pudo conectar con el servidor. Intenta nuevamente en unos minutos."
  - `frontend/src/services/api.js` -> el interceptor global para 5xx usa siempre `SERVER_ERROR_MESSAGE` (mensaje generico), no eco del `data.detail`.
  - Banner offline silenciado cuando `navigator.onLine === false` o `isOfflineOrBackendDown === true` (no muestra toast redundante).

- Suite de tests: 4 tests en `auth.test.js` (`classifyLoginError` cubre sin respuesta / 401 / 5xx / 4xx tecnico / 4xx corto) y 3 tests en `api.test.js` (5xx nunca eco de detalle tecnico, flag `_suppressErrorToast` funciona, 401 sin response muestra mensaje limpio).

## Verificacion

- Branch `fix/issue-51-login-error-classification` mergeada en `main` el 04/07/2026.
- Deploy en `produccion.servinlgsm.com.ar` confirmado via smoke tests.
- Antes: el toast mostraba `pymysql.err.OperationalError: ... SELECT ... FROM usuarios WHERE password_hash = ...`.
- Despues: toast corto y limpio segun el escenario.

## Lecciones aprendidas

- La validacion contra detalle tecnico se hace en frontend (regex `looksTechnical`), no en backend. Esto evita que un cambio futuro en el backend exponga detalles sin querer.
- Para 5xx usamos siempre la constante generica `SERVER_ERROR_MESSAGE`. Esto es intencional: aunque el backend implemente mejor logging (issue #34 abierta), la UI nunca va a leakear SQL/pymysql/etc.
