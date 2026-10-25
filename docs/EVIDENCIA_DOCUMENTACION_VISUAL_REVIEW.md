# Revisión visual — Documentación de la evidencia fotográfica (issue #208)

- **Fecha:** 2026-10-25
- **Rama:** `codex/issue-208-docs-evidencia`
- **Base:** `origin/main` (`bb73897`, PR #207 — aviso por WhatsApp)
- **Alcance visual:** los tres manuales de usuario (operador, encargado, admin)
  con el paso de evidencia, la verificación y el aviso por WhatsApp; los PDF
  que publica la aplicación; y la vista de *Manuales* de la app.

## Comandos ejecutados

```bash
cd frontend
npm test                                     # 389 tests, 0 fallos
npm run check                                # build + PWA
npm run docs:pdf                             # regenera los tres PDF
node scripts/manualesViewCapture.mjs         # captura real de la vista de Manuales
```

```bash
cd backend
venv\Scripts\python.exe -m pytest            # 410 tests, 0 fallos
```

La evidencia del PDF se obtuvo renderizando las páginas con `pypdfium2` y
contando las imágenes embebidas (`pypdf`), no a ojo.

## Flujo probado

1. La app real (Vite + Chromium, con la API interceptada) entra a
   `Manuales` y muestra el manual del rol.
2. Se recorre el manual renderizado en la app: portada, índice, secciones y
   capturas.
3. Se regeneran los tres PDF y se renderizan sus páginas para revisarlas.

## Resultado de los tests

- `npm test`: **389 passed** (388 → 389; 1 nuevo).
- `npm run check`: build OK, PWA generada.
- Backend: **410 tests**, 0 fallos.
- `git diff --check`: limpio.

## Capturas

`docs/screenshots/evidencia_documentacion/` (ver el README de la carpeta).

| Archivo | Qué muestra |
|---|---|
| `manuales-view-1638x969.png` | Vista de *Manuales* de la app, en escritorio. |
| `manuales-view-1638x969-scroll.png` | La misma vista con las capturas del manual cargadas. |
| `manuales-view-390x844.png` | La misma vista en el teléfono. |
| `pdf/01-operador-paso-evidencia-p18.png` | PDF del operador: el paso 7 *Evidencia Fotográfica*. |
| `pdf/02-operador-offline-foto-antes-del-parte-p26.png` | PDF del operador: *La foto viaja antes que el parte*. |
| `pdf/03-encargado-filtro-evidencia-p20.png` | PDF del encargado: el filtro de evidencia. |
| `pdf/04-encargado-seccion-evidencia-p21.png` | PDF del encargado: la sección de evidencia y el aviso por WhatsApp. |
| `pdf/05-admin-flags-de-foto-p10.png` | PDF del admin: los flags de foto por tipo de proceso. |

## Hallazgos

1. **El PDF del manual salía con capturas faltantes.** El renderer marcaba las
   imágenes como `loading="lazy"` y, al imprimir con Chromium, no se
   decodifican las imágenes lazy que están fuera del viewport: en el PDF
   quedaban círculos vacíos en lugar de las capturas. Contadas: faltaban 5
   imágenes del manual del operador, 1 del encargado y 2 del admin. Se quitó el
   `loading="lazy"` y se agregó un test que lo fija. Ahora se pintan **todas**
   (16/16, 15/15 y 10/10).
2. **Había dos versiones distintas de cada manual.** La canónica está en
   `frontend/public/manuales/` (la que publica la app y verifica el CI); en
   `docs/manuales/` había una copia congelada en el commit #106 que ya no
   coincidía. Se eliminó la copia muerta, con sus PDF viejos, y el README de
   la carpeta ahora dice cuál es la fuente.
3. **La vista de *Manuales* de la app sigue bien** después del cambio del
   renderer: 9 capturas visibles, 0 rotas, en 1638x969 y en 390x844.
4. **El PDF grew de 21 a 28 páginas** en el manual del operador: no es que
   grewió el texto, es que ahora las capturas ocupan el lugar que les
   corresponde.

## Veredicto

**aprobado visualmente.** Los tres manuales se leen de corrido, los textos de
la pantalla coinciden con lo que muestra la aplicación, y el PDF que se
publica ya sale con todas las capturas.
