## Contexto

Operador que abre la PWA en campo sin red y nunca inicio sesion antes en este dispositivo ve el banner amber `Sin conexion` arriba del formulario de login, pero no entiende por que no entra directo. Piensa que la app esta rota porque ve "modo offline" pero igual le pide credenciales.

Hoy el banner dice:
> "Sin conexion - Los registros se guardaran localmente y se sincronizaran al reconectar"

Eso es cierto pero incompleto: oculta el requisito de que el operador debe tipear DNI+contraseña **una vez con internet** para que el navegador guarde la sesion offline (sha-256 cache, grace 14 dias).

## Comportamiento esperado

- El `OfflineBanner` (en App.vue) debe comunicar **claramente** que:
  - La app sigue funcionando offline.
  - La primera vez SÍ se requiere internet para validar el DNI una vez.
  - Despues podes entrar sin red durante 14 dias en este dispositivo.

- El `LoginView` cuando el operador esta offline Y no tiene cache offline valido debe mostrar **por que estamos pidiendo credenciales** en lugar de un mensaje generico.

## Tareas

1. `frontend/src/components/ui/OfflineBanner.vue`:
   - Reemplazar el copy del banner a algo como:
     > "Sin conexion - la app sigue funcionando. La primera vez necesitas iniciar sesion con internet; despues podes entrar sin red por 14 dias."
   - Reducir ancho del texto o agregar subline para que sea legible en mobile/desktop.

2. `frontend/src/views/LoginView.vue`:
   - Cuando `navigator.onLine === false` Y `authStore.cachedSession` esta vacio o expirado:
     - Mostrar aviso contextual "Es tu primera vez en este dispositivo: necesitamos senal para validar tu DNI. Despues podes entrar offline hasta por 14 dias."
   - Mantener el aviso generico existente para el caso cache vencido pero presente.

3. Tests:
   - Validar que el copy nuevo aparece cuando corresponde y no aparece cuando online.

## Criterios de aceptacion

- Operador que abre la app sin red ve un mensaje claro de por que tiene que tipear credenciales.
- Operador que ya hizo login online antes no ve el aviso contextual (porque ya tiene cache).
- Operador que vuelve a abrir offline dentro de los 14 dias ve el banner simple sin el subtexto del "primera vez".

## Prioridad

P1 - mejora de UX critica para evitar confusion del operador en campo.

## Archivos clave

- `frontend/src/components/ui/OfflineBanner.vue`
- `frontend/src/views/LoginView.vue`
- `frontend/src/stores/connectivity.js` (para diferenciar online/offline)
