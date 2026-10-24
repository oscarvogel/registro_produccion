# Revisión visual — Evidencia fotográfica en el formulario (issue #200)

- **Fecha:** 2026-10-25
- **Rama:** `codex/issue-200-frontend-evidencia`
- **Base:** `origin/main` (`4102d5f`, PR #199 — API de evidencia)
- **Alcance visual:** el paso nuevo **Evidencia** del wizard de carga de producción.

## Comandos ejecutados

```bash
cd frontend
npm test                                    # 355 tests, 0 fallos
npm run check                               # build + PWA
node scripts/evidenciaFormCapture.mjs       # capturas reales (Playwright + Vite)
```

El script levanta Vite, mockea la API (catálogos, sesión y health check) y
recorre el wizard real hasta el paso de evidencia, con una foto real del repo
cargada en el campo.

## Flujo probado

1. Contexto: la unidad de negocio viene preseleccionada.
2. Operador: precargado (el operador no puede cambiarlo).
3. Equipo: la máquina sale de la asignación del operador.
4. Proceso: `PROCESO` (exige foto del horómetro **y** de la pantalla).
5. Tiempo: 1200 → 1850 (la lectura final tiene que ser **mayor** que la inicial).
6. Producción: 12 m³ y 3 plantas.
7. **Evidencia**: paso nuevo, con la declaración de D7.

## Resultado de los tests

- `npm test`: **355 passed** (335 → 355; 20 nuevos).
- `npm run check`: build OK, PWA generada.
- Desborde horizontal medido por el script: **0 px** en 1638x969, 1366x768 y
  390x844.

## Capturas

`docs/screenshots/evidencia_form/` (ver el README de la carpeta).

| Viewport | Archivos |
|---|---|
| 1638x969 | `01-evidencia-paso-1638x969.png`, `02-evidencia-con-foto-1638x969.png`, `03-evidencia-declaracion-1638x969.png` |
| 1366x768 | idem con sufijo `1366x768` |
| 390x844 | idem con sufijo `390x844` |

## Hallazgos

1. **El paso condicional entra en el lugar correcto.** El indicador de la
   columna izquierda muestra `7 Evidencia ACTUAL` entre *Producción* y
   *Consumos*, y los pasos anteriores quedan en `VALIDADO`. Los pasos se
   identifican por clave (no por número), así que agregar el paso no
   reindexó nada.
2. **La declaración de D7 funciona como se documentó.** Al tildar *"En esa
   misma pantalla se ve el horómetro"*, el campo **Foto del horómetro**
   desaparece y el botón *Siguiente* se habilita: con una sola foto se cubren
   los dos roles (R7).
3. **Sin foto, el paso frena.** Con el campo del procesador vacío aparece el
   error *"Falta la foto de evidencia. No se puede guardar el registro sin
   ella."* y el botón *Siguiente* queda deshabilitado, con el texto de ayuda
   *"Tomá la foto de la pantalla del procesador para continuar."*.
4. **La foto se ve y se puede cambiar.** La miniatura es un recorte de la foto
   real, con *Rehacer foto* y *Quitar*. El subtexto del horómetro muestra la
   lectura que hay que documentar (*"Documentá la lectura final: 1850."*).
5. **El paso no aparece cuando el proceso no exige foto.** El paso se filtra
   por los flags `requiere_foto_horometro` / `requiere_foto_procesador` del
   tipo de proceso; sin flags, el wizard sigue con 9 pasos como antes.
6. **Sin desborde.** El contenido entra entero en 1366x768 (la notebook de la
   planta) y en 390x844 (el teléfono).

## Observaciones (fuera de este issue)

- El rótulo de conectividad del menú lateral dice *"Servidor disponible"*
  porque el script mockea también el health check; en la captura anterior a
  esa corrección decía *"Servidor no disponible"* y era un artefacto del
  entorno de captura (el dev server de Vite no tiene `/health`, que sí está
  en el `nginx.conf.template` de producción).

## Veredicto

**aprobado visualmente.**

El paso se entiende solo en la pantalla de la planta, el operador tiene el
botón de la cámara a mano, y la regla de "una foto alcanza" (D7) queda
explícita en la casilla.
