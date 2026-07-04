## Contexto

Ya existe un banner amarillo de "Sin conexión" en `frontend/src/App.vue:4-14` pero solo aparece cuando el operador ya está autenticado. Cuando el operador abre la app sin red y la app está intentando decidir si dejarlo entrar, no hay feedback visible y queda la sensación de que la app se cuelga.

## Comportamiento esperado

- Si al iniciar la app `navigator.onLine === false`, mostrar el banner amarillo "Sin conexión - usando datos guardados" arriba de todo, incluso antes del router-guard.
- Si el operador estaba autenticado y entra sin red → entra directo a home con banner visible y aviso "X registros pendientes de sincronizar" si los hay.
- Si el operador no estaba autenticado y entra sin red → mostrar login con mensaje "Sin conexión - no se puede validar contra el servidor ahora".

## Tareas

1. Mover el `isOnline` ref de App.vue a `main.js` para tener el dato antes de montar el router.
2. Asegurar que el banner se muestre incluso en `/login` cuando no haya red.
3. Si hay `produccionStore.pendingCount > 0`, mostrar contador en el banner.
4. Test unitario: con `navigator.onLine === false`, el banner es visible en la vista.

## Criterios de aceptación

- En campo sin red, el operador siempre ve el banner amarillo.
- Si ya estaba autenticado, entra directo a home sin pasar por login.
- Si no estaba autenticado, ve login con mensaje claro.

## Prioridad

P1 — mejora la experiencia de UX en offline.
