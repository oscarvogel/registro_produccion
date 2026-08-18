import { readFile, mkdir, access } from 'node:fs/promises'
import { constants } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'
import { renderManualMarkdown } from '../src/services/manualRenderer.js'

const frontendDir = resolve(process.env.DOCS_FRONTEND_DIR || process.cwd())
const manualsDir = join(frontendDir, 'public', 'manuales')
const outputDir = join(manualsDir, 'pdf')
const manualNames = ['manual-operador', 'manual-encargado', 'manual-admin']

const pdfCss = `
  @page { size: A4; margin: 18mm 16mm 18mm; }
  :root { color: #172019; font-family: Arial, Helvetica, sans-serif; }
  * { box-sizing: border-box; }
  body { margin: 0; color: #172019; font-size: 10.5pt; line-height: 1.48; }
  .cover { align-items: center; background: #f2f7f3; border: 1px solid #d6e4da; border-radius: 12px; display: flex; flex-direction: column; justify-content: center; min-height: 238mm; page-break-after: always; text-align: center; }
  .cover img { height: auto; margin-bottom: 12mm; max-width: 68mm; }
  .cover h1 { color: #143d23; font-size: 27pt; line-height: 1.05; margin: 0; }
  .cover .subtitle { color: #217346; font-size: 17pt; font-weight: 700; margin-top: 4mm; }
  .cover .meta { color: #4c5e51; font-size: 10pt; line-height: 1.6; margin-top: 8mm; }
  .page-break { break-after: page; page-break-after: always; height: 0; }
  h1 { color: #143d23; font-size: 20pt; line-height: 1.15; margin: 0 0 7mm; }
  h2 { border-bottom: 1px solid #d6e4da; color: #217346; font-size: 15pt; line-height: 1.2; margin: 9mm 0 3mm; padding-bottom: 1.5mm; page-break-after: avoid; }
  h3 { color: #263c2c; font-size: 12pt; margin: 6mm 0 2mm; page-break-after: avoid; }
  p { margin: 0 0 3mm; }
  ul, ol { margin: 0 0 4mm 7mm; padding-left: 6mm; }
  li { margin: 1mm 0; }
  table { border-collapse: collapse; margin: 4mm 0 5mm; width: 100%; }
  th, td { border: 1px solid #d6e4da; padding: 2.4mm 2.8mm; text-align: left; vertical-align: top; }
  th { background: #f2f7f3; color: #143d23; font-size: 8.5pt; text-transform: uppercase; }
  code { background: #f2f7f3; border: 1px solid #d6e4da; border-radius: 3px; color: #143d23; padding: .2mm 1mm; }
  .warning, .note { border-left: 3px solid #217346; border-radius: 4px; margin: 4mm 0; padding: 3mm 4mm; break-inside: avoid; page-break-inside: avoid; }
  .warning { background: #fff7df; border-left-color: #b77a00; }
  .note { background: #eaf7f0; }
  .manual-screenshot { background: #f7faf8; border: 1px solid #d6e4da; border-radius: 8px; display: block; height: auto; margin: 4mm auto 5mm; max-height: 220mm; max-width: 92%; object-fit: contain; padding: 1.5mm; break-inside: avoid; page-break-inside: avoid; }
`

function imagePathFromSrc(src) {
  if (src === '/logo-forestal.png') return join(frontendDir, 'public', 'logo-forestal.png')
  if (src.startsWith('/manuales/')) return join(frontendDir, 'public', src.slice(1))
  return null
}

async function imageToDataUri(src) {
  const path = imagePathFromSrc(src)
  if (!path) throw new Error(`Imagen no permitida en manual: ${src}`)
  try {
    await access(path, constants.R_OK)
  } catch {
    throw new Error(`Falta la captura o imagen referenciada: ${path}`)
  }
  const data = await readFile(path)
  const mime = path.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg'
  return `data:${mime};base64,${data.toString('base64')}`
}

async function renderManual(name, browser) {
  const markdownPath = join(manualsDir, `${name}.md`)
  const markdown = await readFile(markdownPath, 'utf8')
  let content = renderManualMarkdown(markdown)
  const sources = [...content.matchAll(/<img[^>]+src="([^"]+)"/g)].map((match) => match[1])
  for (const src of new Set(sources)) {
    content = content.replaceAll(`src="${src}"`, `src="${await imageToDataUri(src)}"`)
  }

  const page = await browser.newPage()
  await page.setContent(`<!doctype html><html lang="es"><head><meta charset="utf-8"><style>${pdfCss}</style></head><body>${content}</body></html>`, { waitUntil: 'load' })
  await page.emulateMedia({ media: 'print' })
  await page.pdf({
    path: join(outputDir, `${name}.pdf`),
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="color:#718276;font:8px Arial;width:100%;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    margin: { top: '18mm', right: '16mm', bottom: '18mm', left: '16mm' },
  })
  await page.close()
}

export { imagePathFromSrc, imageToDataUri, renderManual }

async function main() {
  await mkdir(outputDir, { recursive: true })
  const browser = await chromium.launch({ headless: true })
  try {
    for (const name of manualNames) await renderManual(name, browser)
  } finally {
    await browser.close()
  }
  console.log(`PDF generados en ${outputDir}`)
}

const moduleFilePath = import.meta.url.startsWith('file:') ? fileURLToPath(import.meta.url) : null

if (moduleFilePath && process.argv[1] && resolve(process.argv[1]) === moduleFilePath) {
  main().catch((error) => {
    console.error(`[docs:pdf] ${error.message}`)
    process.exitCode = 1
  })
}
