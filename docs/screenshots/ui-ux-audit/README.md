# Auditoria UI/UX - 2026-07-04

## Alcance

Analisis combinado de UX, UI y riesgos de accesibilidad sobre las superficies principales del sistema:

- Login.
- Inicio admin.
- Dashboard operativo.
- Dashboard admin.
- Carga de produccion.
- CRUD admin de personal.

## Evidencia

Capturas guardadas en esta carpeta:

- `01-login-desktop.png`: login desktop, sin sesion.
- `02-home-admin-desktop.png`: inicio admin con datos ficticios.
- `03-dashboard-operativo-desktop.png`: dashboard operativo con datos ficticios.
- `04-admin-dashboard-desktop.png`: dashboard admin con datos ficticios.
- `05-produccion-form-desktop.png`: carga de produccion desktop con datos ficticios.
- `06-admin-personal-desktop.png`: CRUD de personal con datos ficticios.
- `07-produccion-form-mobile.png`: carga de produccion mobile con datos ficticios.

## Metodo

El backend local respondio saludable en `127.0.0.1:8004` y el frontend en `127.0.0.1:5174`.
No habia credenciales demo validas disponibles para ingresar contra la base local.
Browser y Chrome del entorno Codex no estaban disponibles, por lo que las capturas se generaron con Playwright local contra el frontend servido.

Pantallas internas: sesion admin simulada en `localStorage` y respuestas `/api/` mockeadas con datos ficticios, sin tocar datos reales.

## Hallazgos Criticos

1. **Duplicacion de modelos de dashboard**

   `Inicio`, `Dashboard Operativo` y `Dashboard Admin` muestran metricas, filtros, rankings y actividad reciente con estructuras parecidas pero nombres y jerarquia distintos. Esto obliga al admin a aprender tres formas de leer informacion similar.

   Recomendacion: definir una arquitectura de informacion unica: `Inicio` como resumen accionable, `Dashboard Operativo` para analisis por unidad/equipo, y `Dashboard Admin` como vista ejecutiva. Evitar repetir KPIs y rankings sin explicar para que sirve cada vista.

2. **Navegacion lateral con secciones cerradas oculta tareas clave**

   En escritorio el menu muestra `Operacion`, `Catalogos`, `Combustible` y `Produccion` como grupos cerrados. Para usuarios nuevos, acciones frecuentes como carga, pendientes, personal o dashboard quedan escondidas hasta expandir.

   Recomendacion: dejar abiertas por defecto las secciones relevantes para el rol o mostrar acciones primarias persistentes. Para admin, `Dashboard`, `Carga`, `Pendientes` y `Personal` deberian estar a un click visible.

3. **Densidad alta y baja separacion entre lectura y accion**

   En dashboards hay filtros, chips, KPIs, tablas, graficos, comparativas y botones en el primer viewport. La informacion es rica, pero cuesta decidir que mirar primero y que accion tomar.

   Recomendacion: ordenar por prioridad operacional: estado del periodo, alerta principal, KPI dominante, acciones recomendadas y detalle secundario. Reducir elementos simultaneos en el primer viewport.

4. **CRUD admin con riesgo de error en acciones sensibles**

   En `Personal`, editar y desactivar estan muy cerca y ambos aparecen como acciones de fila. Ademas, la primera fila renderizo `Si` en la columna `ID`, lo que sugiere un problema de mapeo visible.

   Recomendacion: separar acciones destructivas, pedir confirmacion contextual con nombre/DNI, y corregir el mapeo de ID. En pantallas de permisos/personas, los errores son de alto impacto.

5. **Carga guiada clara, pero con friccion por longitud**

   El flujo de produccion tiene buena estructura visual: paso actual, estado de borrador y CTA claro. El riesgo es que 9 pasos generan carga cognitiva y el resumen superior solo repite `Pendiente` sin indicar que falta para avanzar.

   Recomendacion: marcar el bloqueo puntual por paso, agrupar pasos si el proceso lo permite, y mostrar validaciones preventivas junto al CTA `Siguiente`.

6. **Riesgos de accesibilidad por contraste y dependencia cromatica**

   El modo oscuro tiene buen caracter visual, pero varios textos secundarios y estados usan verdes/grises de bajo contraste sobre fondo oscuro. Algunos estados se comunican principalmente por color.

   Recomendacion: revisar contraste WCAG en chips, subtitulos, labels de tablas, placeholders y estados. Acompanar color con texto/icono/forma y probar navegacion por teclado.

7. **Inconsistencias de idioma y acentos visibles**

   Se observan textos con problemas de codificacion o variantes sin acento: `Produccion`, `Contrasena`, `Ultimos`, junto con otros bien acentuados.

   Recomendacion: normalizar encoding y copy visible. En una app operativa, estas inconsistencias bajan confianza y hacen mas dificil el uso por personal no tecnico.

## Prioridad Recomendada

1. Corregir CRUD admin de personal: mapeo de ID, acciones sensibles y confirmaciones.
2. Reordenar navegacion por rol para que las tareas frecuentes no queden ocultas.
3. Consolidar la funcion de cada dashboard y reducir duplicacion visible.
4. Mejorar validaciones y mensajes de bloqueo en carga de produccion.
5. Auditar contraste, foco teclado, estados y copy/encoding.

## Limites

Estas capturas validan estructura visual y comportamiento basico de pantallas, no cumplimiento WCAG completo ni datos reales de produccion.
Para una auditoria completa faltaria probar con credenciales reales o demo validas, teclado, lector de pantalla, estados offline reales y formularios completos hasta guardado/sincronizacion.
