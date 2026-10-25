// Captura real de la vista de Manuales de la aplicacion.
//
// El issue #208 quito el `loading="lazy"` de las imagenes del manual
// (manualRenderer.js): al imprimir el PDF con Chromium, las imagenes lazy
// fuera del viewport no se pintaban y el PDF salia con capturas faltantes.
//
// Este script verifica que la vista de Manuales de la app sigue renderizando
// el manual (con sus capturas) despues del cambio.
//
// Uso:
//   node scripts/manualesViewCapture.mjs
import { spawn } from 'node:child_process'
import { mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { chromium } from 'playwright'

const frontendDir = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repoDir = resolve(frontendDir, '..')
const outputDir = join(repoDir, 'docs', 'screenshots', 'evidencia_documentacion')
const host = '127.0.0.1'
const port = Number(process.env.DOCS_CAPTURE_PORT || 4176)
const baseUrl = `http://${host}:${port}`

const sleep = (ms) => new Promise((resolve_) => setTimeout(resolve_, ms))

function jsonResponse(route, body, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    headers: { 'access-control-allow-origin': '*' },
    body: JSON.stringify(body),
  })
}

function makeToken() {
  const encode = (value) => Buffer.from(JSON.stringify(value)).toString('base64url')
  return `${encode({ alg: 'HS256' })}.${encode({ sub: '90000003', dni: '90000003' })}.firma`
}

const ADMIN = {
  idPersonal: 103,
  Nombre: 'ADMIN DEMO',
  dni: '90000003',
  activo: 1,
  encargado: 0,
  is_admin: 1,
  unidad_negocio: 144,
}

async function mockApi(route) {
  const url = new URL(route.request().url())
  const path = url.pathname
  const method = route.request().method()

  if (method === 'OPTIONS') return route.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*' } })

  if (path === '/api/auth/login') {
    return jsonResponse(route, { access_token: makeToken(), user: ADMIN })
  }
  if (path === '/api/health' || path === '/health') return jsonResponse(route, { status: 'ok', database: 'ok' })
  if (path.includes('/sincronizar') || path.includes('/catalogos')) {
    return jsonResponse(route, { message: 'Catálogos sincronizados', total_activos: 3 })
  }
  if (path.startsWith('/api/')) return jsonResponse(route, [])
  return route.continue()
}

async function startVite() {
  const viteEntry = join(frontendDir, 'node_modules', 'vite', 'bin', 'vite.js')
  const child = spawn(process.execPath, [viteEntry, '--host', host, '--port', String(port)], {
    cwd: frontendDir,
    stdio: 'ignore',
    windowsHide: true,
  })
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const response = await fetch(baseUrl)
      if (response.ok) return child
    } catch {
      // Vite todavia esta arrancando.
    }
    await sleep(250)
  }
  child.kill()
  throw new Error(`No se pudo levantar Vite en ${baseUrl}.`)
}

async function main() {
  mkdirSync(outputDir, { recursive: true })
  console.log(`[manuales:capture] iniciando en ${baseUrl}`)
  const vite = await startVite()
  const browser = await chromium.launch({ headless: true })
  const errores = []
  let fallos = 0

  try {
    const viewports = [
      { nombre: '1638x969', width: 1638, height: 969 },
      { nombre: '390x844', width: 390, height: 844 },
    ]

    for (const viewport of viewports) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        locale: 'es-AR',
        colorScheme: 'light',
        serviceWorkers: 'block',
      })
      const page = await context.newPage()
      page.on('pageerror', (error) => errores.push(`${viewport.nombre}: ${error.message}`))
      await page.route('**/api/**', (route) => mockApi(route))
      await page.route((url) => url.pathname === '/health', (route) => mockApi(route))

      // Login. Hay dos formularios (escritorio y movil): se usa el visible.
      await page.goto(`${baseUrl}/login`)
      await page.waitForLoadState('domcontentloaded')
      await page.waitForTimeout(400)
      const dni = page.locator('#mobile-dni:visible, #desktop-dni:visible').first()
      const password = page.locator('#mobile-password:visible, #desktop-password:visible').first()
      await dni.fill('90000003')
      await password.fill('demo-admin')
      await page.locator('button:visible').filter({ hasText: 'Ingresar' }).first().click()
      await page.waitForURL(`${baseUrl}/`)
      await page.waitForTimeout(500)

      // Vista de manuales
      await page.goto(`${baseUrl}/manuales`)
      await page.waitForLoadState('domcontentloaded')
      await page.waitForTimeout(1800)

      const texto = await page.locator('body').innerText()
      const capturas = await page.locator('img.manual-screenshot').count()
      const rotas = await page.evaluate(() =>
        Array.from(document.querySelectorAll('img.manual-screenshot')).filter(
          (img) => !img.complete || img.naturalWidth === 0,
        ).length,
      )

      const hayContenido = texto.includes('Carga de Producción') || texto.includes('Manual de Usuario')
      const ok = hayContenido && capturas > 0 && rotas === 0
      if (!ok) fallos += 1
      console.log(
        `  [${ok ? 'OK ' : 'FALLA'}] ${viewport.nombre}: capturas=${capturas} rotas=${rotas} contenido=${hayContenido}`,
      )

      await page.screenshot({ path: join(outputDir, `manuales-view-${viewport.nombre}.png`), fullPage: false })
      await page.evaluate(() => window.scrollTo(0, 1200))
      await page.waitForTimeout(600)
      await page.screenshot({ path: join(outputDir, `manuales-view-${viewport.nombre}-scroll.png`), fullPage: false })

      await context.close()
    }
  } finally {
    await browser.close()
    if (vite) vite.kill()
  }

  if (errores.length) {
    console.log(`[manuales:capture] errores de pagina: ${errores.length}`)
    for (const error of errores) console.log(`  - ${error}`)
  }

  console.log(fallos === 0 ? '[manuales:capture] OK' : `[manuales:capture] FALLARON ${fallos} viewports`)
  process.exitCode = fallos === 0 && errores.length === 0 ? 0 : 1
}

main().catch((error) => {
  console.error(`[manuales:capture] ${error.message}`)
  process.exitCode = 1
})
