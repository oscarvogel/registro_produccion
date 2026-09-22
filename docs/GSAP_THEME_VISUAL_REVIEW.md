# Revisión visual: GSAP y transición de tema

Fecha: 2026-09-16

## Alcance implementado

- GSAP integrado como capa complementaria de las transiciones CSS, `@vueuse/motion` y `TransitionGroup` existentes.
- Cambio oscuro/claro con `document.startViewTransition()` cuando está disponible y fallback directo cuando no lo está.
- Icono de tema con rotación y escala breve, sin desplazar el contenido.
- Entradas coordinadas en Login, Home y Dashboard.
- Flip para cambios de layout en unidades, rankings, registros y colas operativas.
- ScrollTrigger limitado a gráficos y ranking del Dashboard, con ejecución única y sin `pin` ni `scrub`.
- Respeto de `prefers-reduced-motion`, foco y zoom/reflow.

## Evidencia automatizada

Ejecutado desde `frontend/`:

```text
npm test       -> 50 archivos, 293 tests aprobados
npm run build  -> build de producción aprobado
git diff --check -> sin errores de whitespace
```

Los warnings observados corresponden a directivas de motion no registradas en algunos tests existentes, una importación dinámica/estática de `toast.js`, el tamaño de un chunk y datos de Browserslist desactualizados. No bloquearon la suite ni el build.

## Evidencia visual

Se inspeccionó la aplicación local en Edge y se capturaron estados reproducibles a 1440 px y 390 px:

- [Login escritorio oscuro](screenshots/gsap-theme/login-desktop-dark.png)
- [Login móvil oscuro](screenshots/gsap-theme/login-mobile-dark.png)
- [Login móvil claro](screenshots/gsap-theme/login-mobile-light.png)

Resultados observados:

- El Login mantiene una entrada coordinada y una jerarquía clara.
- A 390 px el contenido refluye en una sola columna sin overflow horizontal visible.
- El tema claro conserva campos, botones, bordes y textos legibles.
- El zoom aumentado del navegador mantiene accesibles los campos y acciones principales, aunque el flujo vertical requiere desplazamiento normal.
- El acceso directo a `/dashboard` redirige a `/login` al no existir una sesión autenticada en el entorno de validación. Por ello, la validación visual autenticada de Dashboard, Home, Configuración, formularios y listas queda pendiente de ejecutarse con una cuenta de prueba o una sesión autorizada.

## Referencias

- [MDN: View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)
- [MDN: Using View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using)
- [GSAP: Core / timelines](https://gsap.com/docs/v3/GSAP/)
- [GSAP: Flip](https://gsap.com/docs/v3/Plugins/Flip/)
- [GSAP: ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)
- [GSAP: `matchMedia()`](https://gsap.com/docs/v3/GSAP/gsap.matchMedia%28%29/)
- [GSAPify: Animation references](https://gsapify.com/gsap-animations/)
