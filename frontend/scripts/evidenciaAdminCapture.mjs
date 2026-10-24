// Captura visual del Admin de Tipos de Proceso con los flags de evidencia
// fotografica (issue #194).
//
// Usa la API mockeada y Vite, igual que scripts/camionetaCapture.mjs, para
// generar screenshots reales sin base de datos.
//
//   node scripts/evidenciaAdminCapture.mjs
//
// Salida: docs/screenshots/evidencia_admin/

import { existsSync, mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { spawn } from 'node:child_process'
import { setTimeout as sleep } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const frontendDir = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repoDir = resolve(frontendDir, '..')
const outputRoot = process.env.EVIDENCIA_CAPTURE_OUT
  ? resolve(process.env.EVIDENCIA_CAPTURE_OUT)
  : join(repoDir, 'docs', 'screenshots', 'evidencia_admin')
const host = '127.0.0.1'
const port = Number(process.env.EVIDENCIA_CAPTURE_PORT || 4177)
const baseUrl = process.env.EVIDENCIA_CAPTURE_BASE_URL || `http://${host}:${port}`

// Viewports que usa el cliente (ver seccion 11 de AGENTS.md).
const VIEWPORTS = [
  { key: '1638x969', width: 1638, height: 969 },
  { key: '1366x768', width: 1366, height: 768 },
  { key: '390x844', width: 390, height: 844 },
]

// Datos reales: en la base, los tipos de proceso de produccion estan
// vinculados a la UN 144 "Caminos". El nombre corto importa para medir el
// ancho de la grilla.
const UN = { idUnidadNegocio: 144, nombre: 'Caminos', prefijo: 'CAM', codigo_kobo: 'caminos', activo: 1 }

// Reproduce la configuracion inicial de la decision D8.
const TIPOS_PROCESO = [
  {
    id: 3,
    nombre: 'PROCESO',
    campos: 'm3,plantas',
    unidad_ids: [144],
    requiere_acta: false,
    requiere_predio: false,
    requiere_rodal: false,
    requiere_horometro: true,
    requiere_foto_horometro: true,
    requiere_foto_procesador: true,
    activo: 1,
  },
  {
    id: 4,
    nombre: 'VOLTEO',
    campos: 'plantas',
    unidad_ids: [144],
    requiere_acta: false,
    requiere_predio: false,
    requiere_rodal: false,
    requiere_horometro: true,
    requiere_foto_horometro: false,
    requiere_foto_procesador: true,
    activo: 1,
  },
  {
    id: 5,
    nombre: 'HORAS MAQUINAS',
    campos: 'hora_inicio,hora_fin',
    unidad_ids: [144],
    requiere_acta: false,
    requiere_predio: false,
    requiere_rodal: false,
    requiere_horometro: true,
    requiere_foto_horometro: true,
    requiere_foto_procesador: false,
    activo: 1,
  },
  {
    id: 1,
    nombre: 'CARGA',
    campos: 'tn_despachadas',
    unidad_ids: [144],
    requiere_acta: false,
    requiere_predio: false,
    requiere_rodal: false,
    requiere_horometro: true,
    requiere_foto_horometro: false,
    requiere_foto_procesador: false,
    activo: 1,
  },
]

const ADMIN_USER = {
  idPersonal: 103,
  nombre: 'ADMIN DEMO',
  encargado: 0,
  is_admin: 1,
  unidad_negocio: 1,
  unidad_ids: [1],
}

function jsonResponse(route, body, status = 200) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function makeToken() {
  const encode = (value) => Buffer.from(JSON.stringify(value)).toString('base64url')
  return `${encode({ alg: 'none', typ: 'JWT' })}.${encode({ exp: 4102444800, sub: 'evidencia-demo' })}.demo`
}

async function mockApi(route) {
  const request = route.request()
  const path = new URL(request.url()).pathname
  const method = request.method()

  if (path === '/api/auth/login' && method === 'POST') {
    return jsonResponse(route, { access_token: makeToken(), user: ADMIN_USER })
  }
  if (path === '/api/health') return jsonResponse(route, { status: 'ok', instance: 'demo' })
  if (path === '/api/admin/unidades-negocio') return jsonResponse(route, [UN])
  if (path === '/api/admin/tipos-proceso' && method === 'GET') return jsonResponse(route, TIPOS_PROCESO)
  if (path === '/api/admin/tipos-proceso' && method === 'POST') return jsonResponse(route, TIPOS_PROCESO[0])
  if (path.startsWith('/api/')) return jsonResponse(route, [])
  return route.continue()
}

async function seedSession(context, user) {
  await context.addInitScript((payload) => {
    localStorage.setItem('token', payload.token)
    localStorage.setItem('user', JSON.stringify(payload.user))
    localStorage.setItem('catalogos_sync_ok', '1')
  }, { token: makeToken(), user })
}

async function waitForApp(page) {
  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(500)
  await page.evaluate(() => window.scrollTo(0, 0))
}

async function capture(page, name, { fullPage = true } = {}) {
  mkdirSync(outputRoot, { recursive: true })
  await page.waitForTimeout(250)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: join(outputRoot, name), fullPage })
}

// Mide si la grilla desborda el ancho disponible: sirve para verificar que
// la columna de acciones no queda fuera de pantalla en las resoluciones del
// cliente (ver seccion 11 de AGENTS.md).
async function measureOverflow(page) {
  return page.evaluate(() => {
    const container = document.querySelector('.app-table')
    if (!container) return null
    const table = container.querySelector('table')
    const headers = Array.from(table?.querySelectorAll('thead th') || []).map((th) => ({
      label: th.innerText.trim().slice(0, 22),
      width: Math.round(th.getBoundingClientRect().width),
    }))
    return {
      visible: container.clientWidth,
      needed: table ? table.scrollWidth : container.scrollWidth,
      overflow: Math.max(0, (table ? table.scrollWidth : container.scrollWidth) - container.clientWidth),
      headers,
    }
  })
}

function visibleLocator(page, selector) {
  return page.locator(`${selector}:visible`)
}

async function captureListado(browser, viewport) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    locale: 'es-AR',
    colorScheme: 'dark',
    // El service worker de la PWA intercepta /api/... y esquiva el mock.
    serviceWorkers: 'block',
  })
  await seedSession(context, ADMIN_USER)
  const page = await context.newPage()
  page.on('pageerror', (error) => console.error(`[evidencia] error de pagina: ${error.message}`))
  await page.route('**/api/**', (route) => mockApi(route))

  await page.goto(`${baseUrl}/admin/crud/tipos-proceso`)
  await waitForApp(page)
  await page.waitForTimeout(900)
  const medidas = await measureOverflow(page)
  console.log(
    `[evidencia] ${viewport.key}: visible=${medidas?.visible}px necesario=${medidas?.needed}px ` +
      `desborde=${medidas?.overflow}px`,
  )
  if (medidas?.headers) {
    console.log(
      `[evidencia] ${viewport.key} columnas: ` +
        medidas.headers.map((h) => `${h.label}=${h.width}`).join(' | '),
    )
  }
  await capture(page, `01-admin-tipos-lista-${viewport.key}.png`)
  await context.close()
}

async function captureFormulario(browser, viewport) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    locale: 'es-AR',
    colorScheme: 'dark',
    serviceWorkers: 'block',
  })
  await seedSession(context, ADMIN_USER)
  const page = await context.newPage()
  page.on('pageerror', (error) => console.error(`[evidencia] error de pagina: ${error.message}`))
  await page.route('**/api/**', (route) => mockApi(route))

  await page.goto(`${baseUrl}/admin/crud/tipos-proceso`)
  await waitForApp(page)
  await page.waitForTimeout(900)

  const nuevo = page.getByRole('button', { name: 'Nuevo', exact: true }).first()
  if (!(await nuevo.count())) throw new Error('No se encontro el boton Nuevo')
  await nuevo.click()
  await page.waitForTimeout(600)

  const requisitos = page.getByRole('button', { name: 'Requisitos', exact: true }).first()
  if (!(await requisitos.count())) throw new Error('No se encontro la seccion Requisitos')
  await requisitos.click()
  await page.waitForTimeout(500)

  // Se marcan los dos flags de evidencia para que la captura muestre los
  // checkboxes con el estado que(admin) configura.
  const fotoHorometro = page.locator('#requiere_foto_horometro')
  const fotoProcesador = page.locator('#requiere_foto_procesador')
  if (await fotoHorometro.count()) await fotoHorometro.check({ force: true }).catch(() => {})
  if (await fotoProcesador.count()) await fotoProcesador.check({ force: true }).catch(() => {})
  await page.waitForTimeout(300)

  await capture(page, `02-admin-requisitos-evidencia-${viewport.key}.png`)
  await context.close()
}

async function startVite() {
  if (process.env.EVIDENCIA_CAPTURE_BASE_URL) return null
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
      // Vite still starting
    }
    await sleep(250)
  }
  child.kill()
  throw new Error(`No se pudo levantar Vite en ${baseUrl}.`)
}

async function main() {
  console.log(`[evidencia] iniciando en ${baseUrl}`)
  const vite = await startVite()
  const browser = await chromium.launch({ headless: true })
  try {
    for (const viewport of VIEWPORTS) {
      await captureListado(browser, viewport)
      await captureFormulario(browser, viewport)
    }
  } finally {
    await browser.close()
    if (vite) vite.kill()
  }

  const required = VIEWPORTS.flatMap((viewport) => [
    `01-admin-tipos-lista-${viewport.key}.png`,
    `02-admin-requisitos-evidencia-${viewport.key}.png`,
  ])
  const missing = required.filter((name) => !existsSync(join(outputRoot, name)))
  if (missing.length) throw new Error(`Faltan capturas: ${missing.join(', ')}`)
  console.log(`[evidencia] capturas en ${outputRoot}`)
}

main().catch((error) => {
  console.error(`[evidencia] ${error.message}`)
  process.exitCode = 1
})
