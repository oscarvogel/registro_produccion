# Revisión visual de manuales

- Fecha: 2026-08-18
- Rama: `feat/issue-148-manuales-pdf-playwright`
- Commits de la revisión: `70419d5` (tooling) y `e233d21` (manuales y artefactos)
- Veredicto: **aprobado visualmente**

## Flujo probado

Se ejecutó el capture mock con Playwright Chromium en viewport móvil de 390 × 844 para los roles `operador`, `encargado` y `admin`. Se verificaron login, sincronización, inicio, menú móvil, los nueve pasos del formulario de producción, pendientes y la pantalla adicional de cada rol.

Los datos son ficticios y están identificados como demo: unidad `UNIDAD DEMO FORESTAL`, equipo `MAQUINA DEMO 01`, patente `DEMO-01`, proceso `PROCESO DEMO` y usuarios demo sin credenciales reales.

## Evidencia

- 47 capturas Playwright en `docs/manuales/capturas/`.
- 47 copias públicas en `frontend/public/manuales/capturas/`.
- `manual-operador.pdf`: 27 páginas A4.
- `manual-encargado.pdf`: 22 páginas A4.
- `manual-admin.pdf`: 17 páginas A4.
- Se renderizaron y revisaron visualmente las portadas y páginas interiores con capturas incrustadas de los tres PDFs.

## Comandos ejecutados

```text
npm run docs:capture
npm run docs:pdf
npx vitest run src/services/manualAssets.test.js src/services/manualRenderer.test.js scripts/docsPdf.test.js --reporter=dot
npm run test
npm run build
git diff --check
```

Resultados: capture mock OK; generación PDF OK; tests focalizados 3 suites / 26 tests OK; suite completa 33 archivos / 250 tests OK; build OK. El build conserva únicamente warnings existentes sobre chunks grandes y la importación dinámica/estática de `toast.js`.

## Hallazgos

- Las imágenes locales se renderizan en Markdown y PDF, con validación de existencia.
- Los PDFs incluyen portada, numeración, formato A4 y capturas legibles.
- No se modificaron reglas de negocio, datos productivos, endpoints productivos ni credenciales.
- No se ejecutó modo real: el capture está cerrado a fixtures mock salvo una configuración externa explícita y segura.
