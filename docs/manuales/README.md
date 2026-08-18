# Manuales de usuario

Esta carpeta contiene la documentación funcional y las capturas móviles del issue #148. Las capturas se toman sobre la aplicación Vue real, con viewport `390x844` y APIs ficticias interceptadas por Playwright. No se usa la base de datos de producción.

## Dependencias

- Node.js y npm.
- Dependencias del frontend instaladas con `npm install`.
- Playwright y Chromium, instalados por `npm install` y `npx playwright install chromium`.
- Un navegador compatible con la revisión visual de los PDFs. Para renderizar páginas desde consola se recomienda Poppler (`pdftoppm`).

## Preparación

Desde `frontend/`:

```powershell
npm install
npx playwright install chromium
```

La captura usa por defecto un mock local seguro. Las credenciales son fixtures claramente ficticios y sólo sirven para que el script atraviese la pantalla de login:

| Rol | DNI ficticio | Contraseña ficticia |
| --- | --- | --- |
| Operador | `90000001` | `demo-operador` |
| Encargado | `90000002` | `demo-encargado` |
| Admin | `90000003` | `demo-admin` |

Los datos visibles también son ficticios: `OPERADOR DEMO`, `MAQUINA DEMO 01`, `UNIDAD DEMO FORESTAL`, `1001`, `PREDIO DEMO` y `R-01`.

## Levantar la aplicación

En una terminal:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5174
```

La aplicación queda disponible en `http://127.0.0.1:5174`. El backend no es necesario para el modo mock de documentación.

## Capturas

Con Vite levantado, desde `frontend/`:

```powershell
$env:DOCS_CAPTURE_BASE_URL = 'http://127.0.0.1:5174'
npm run docs:capture
```

El script genera las capturas de operador, encargado y admin en `docs/manuales/capturas/`. Antes de cada imagen espera la navegación, usa un viewport móvil determinístico y desactiva animaciones. El script falla con un mensaje claro si falta configuración del modo solicitado o si falta una captura obligatoria.

Para actualizar sólo un rol durante una iteración:

```powershell
$env:DOCS_CAPTURE_ROLES = 'encargado'
npm run docs:capture
Remove-Item Env:DOCS_CAPTURE_ROLES
```

Antes de publicar, ejecutar la captura completa sin `DOCS_CAPTURE_ROLES` para validar los tres roles.

## Regenerar PDFs

Los PDFs se generan directamente desde los tres Markdown y las imágenes existentes:

```powershell
npm run docs:pdf
```

Los archivos finales quedan en `frontend/public/manuales/pdf/`. La generación usa A4, portada, índice escrito en la fuente Markdown, márgenes, saltos de página, imágenes sin corte y pie con número de página. Si una imagen referenciada no existe, el comando falla antes de crear un PDF incompleto.

Para ejecutar todo el ciclo:

```powershell
npm run docs:build
```

## Actualizar una captura puntual

1. Revisá el flujo correspondiente en `frontend/scripts/docsCapture.mjs`.
2. Ejecutá el rol con `DOCS_CAPTURE_ROLES` para evitar esperar los otros roles durante la iteración.
3. Confirmá que el PNG se guardó con el mismo nombre.
4. Revisá el Markdown que lo referencia.
5. Ejecutá `npm run docs:pdf` para regenerar los tres PDFs.

No reemplaces una captura real por una imagen editada manualmente ni agregues datos reales.

## Verificación visual

Después de generar los PDFs, renderizá sus páginas a PNG con Poppler:

```powershell
New-Item -ItemType Directory -Force tmp/pdfs | Out-Null
pdftoppm -png frontend/public/manuales/pdf/manual-operador.pdf tmp/pdfs/operador
pdftoppm -png frontend/public/manuales/pdf/manual-encargado.pdf tmp/pdfs/encargado
pdftoppm -png frontend/public/manuales/pdf/manual-admin.pdf tmp/pdfs/admin
```

Revisá portada, índice, títulos, saltos, imágenes, márgenes, legibilidad y pies de página. No debe haber páginas en blanco, capturas deformadas o contenido fuera del A4.

## Validaciones

Desde `frontend/`:

```powershell
npm run test
npm run build
```

Las pruebas comprueban la existencia de Markdown, PDF y capturas, las referencias locales, las rutas configuradas en `ManualesView.vue` y el fallo claro cuando falta una imagen obligatoria. El repositorio no tiene un script `lint` dedicado; `npm run build` funciona como verificación de compilación del frontend.

## Archivos que se versionan

Se deben versionar las fuentes Markdown, los scripts de captura y PDF, esta guía, las capturas finales y los tres PDFs finales. No se deben versionar credenciales, cookies, bases de datos, perfiles, videos, trazas ni archivos temporales.
