// Captura visual del flujo camioneta (KM + combustible, sin horometro).
// Usa la API mockeada y Vite, igual que docsCapture.mjs, para generar
// screenshots reales sin base de datos.
//
//   node scripts/camionetaCapture.mjs
//
// Salida: docs/screenshots/camioneta_km_combustible/

import { copyFileSync, existsSync, mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { spawn } from 'node:child_process'
import { setTimeout as sleep } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const frontendDir = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repoDir = resolve(frontendDir, '..')
const outputRoot = join(repoDir, 'docs', 'screenshots', 'camioneta_km_combustible')
const host = '127.0.0.1'
const port = Number(process.env.CAMIONETA_CAPTURE_PORT || 4176)
const baseUrl = process.env.CAMIONETA_CAPTURE_BASE_URL || `http://${host}:${port}`
const viewport = { width: 1440, height: 900, deviceScaleFactor: 1 }

const UN = { idUnidadNegocio: 1, nombre: 'UNIDAD NEGOCIO DEMO FORESTAL', prefijo: 'DEM', codigo_kobo: 'demo', activo: 1 }
const OPERADOR = { idPersonal: 101, nombre: 'OPERADOR DEMO 01', unidad_negocio: 1, tipo_de_proceso_id: 900003 }
const MOVIL = { idMovil: 900001, detalle: 'MOVIL DEMO 01', patente: 'DEM001', unidad_negocio: 1 }
const CAMIONETA = {
  id: 900003,
  nombre: 'CAMIONETA DEMO',
  campos: '',
  requiere_acta: false,
  requiere_predio: false,
  requiere_rodal: false,
  requiere_horometro: false,
  activo: 1,
  unidad_ids: [1],
}
const ASIGNACION = { idAsignacion: 1, idMovil: 900001, patente: 'DEM001', detalle: 'MOVIL DEMO 01', idProceso: 900003 }
const LUGAR_CARGA = { idLugarCarga: 900001, detalle: 'LUGAR CARGA DEMO 01' }

const OPERADOR_USER = {
  idPersonal: 101,
  nombre: 'OPERADOR DEMO 01',
  encargado: 0,
  is_admin: 0,
  unidad_negocio: 1,
  unidad_ids: [1],
  tipo_de_proceso_id: 900003,
}
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
  return `${encode({ alg: 'none', typ: 'JWT' })}.${encode({ exp: 4102444800, sub: 'camioneta-demo' })}.demo`
}

async function mockApi(route) {
  const request = route.request()
  const url = new URL(request.url())
  const path = url.pathname
  const method = request.method()

  if (path === '/api/auth/login' && method === 'POST') {
    return jsonResponse(route, { access_token: makeToken(), user: OPERADOR_USER })
  }
  if (path === '/api/health') return jsonResponse(route, { status: 'ok', instance: 'demo' })
  if (path === '/api/produccion/unidades-negocio') return jsonResponse(route, [UN])
  if (path === '/api/produccion/operadores') return jsonResponse(route, [OPERADOR])
  if (path === '/api/produccion/moviles') return jsonResponse(route, [MOVIL])
  if (path === '/api/produccion/tipo-proceso' || path === '/api/produccion/tipos-proceso-all') {
    return jsonResponse(route, [CAMIONETA])
  }
  if (path === '/api/produccion/lugares-carga') return jsonResponse(route, [LUGAR_CARGA])
  if (path.includes('/api/produccion/asignaciones/')) return jsonResponse(route, [ASIGNACION])
  if (path.includes('/api/produccion/movil-by-operador/')) return jsonResponse(route, MOVIL)
  if (path === '/api/produccion/ultima-hora-fin') return jsonResponse(route, { hr_fin: null })
  if (path === '/api/produccion/actas') return jsonResponse(route, [])
  if (path === '/api/produccion/predios') return jsonResponse(route, [])
  if (path === '/api/produccion/rodales') return jsonResponse(route, [])
  if (path === '/api/produccion/mis-registros') {
    return jsonResponse(route, {
      registros: [{
        id: 900201,
        fecha: '2026-10-16',
        operacion: 'CAMIONETA DEMO',
        equipo: 'MOVIL DEMO 01 - DEM001',
        unidad: 'UNIDAD NEGOCIO DEMO FORESTAL',
        operador: 'OPERADOR DEMO 01',
        hr_inicio: 0,
        hr_fin: 0,
        combustible: 45,
        observaciones: 'Carga de combustible y KM',
      }],
      child_ids: [],
    })
  }
  if (path === '/api/produccion/' && method === 'POST') return jsonResponse(route, { id: 900201 })
  if (path === '/api/admin/unidades-negocio') return jsonResponse(route, [UN])
  if (path === '/api/admin/tipos-proceso' && method === 'GET') return jsonResponse(route, [CAMIONETA])
  if (path === '/api/admin/tipos-proceso' && method === 'POST') return jsonResponse(route, CAMIONETA)
  if (path.startsWith('/api/admin/')) return jsonResponse(route, [])
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
  await page.waitForTimeout(400)
  await page.evaluate(() => window.scrollTo(0, 0))
}

async function capture(page, name, { fullPage = true } = {}) {
  mkdirSync(outputRoot, { recursive: true })
  await page.waitForTimeout(250)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: join(outputRoot, name), fullPage })
}

function visibleLocator(page, selector) {
  return page.locator(`${selector}:visible`)
}

async function choose(page, labelText, value) {
  const label = visibleLocator(page, 'label').filter({ hasText: labelText }).first()
  const field = label.locator('..').locator('input[role="combobox"]')
  await field.fill(value)
  await page.getByRole('option', { name: new RegExp(value, 'i') }).first().click()
  await page.waitForTimeout(250)
}

async function fillField(page, labelText, value) {
  const label = visibleLocator(page, 'label').filter({ hasText: labelText }).first()
  await label.locator('..').locator('input, textarea').fill(String(value))
}

async function next(page) {
  await page.getByRole('button', { name: 'Siguiente', exact: true }).click()
  await page.waitForTimeout(300)
}

async function captureOperador(browser) {
  const context = await browser.newContext({ viewport, locale: 'es-AR', colorScheme: 'dark' })
  await seedSession(context, OPERADOR_USER)
  const page = await context.newPage()
  page.on('pageerror', (error) => console.error(`[camioneta] error de pagina: ${error.message}`))
  await page.route('**/api/**', (route) => mockApi(route))

  await page.goto(`${baseUrl}/produccion`)
  await waitForApp(page)
  await page.waitForTimeout(800)
  await capture(page, '01-parte-contexto.png')

  await next(page)
  await capture(page, '02-parte-operador.png')

  await next(page)
  // Equipo: si el operador ya trae asignaciones, se elige el movil; si no,
  // se lo busca en el buscador de maquinas.
  const asignacionBtn = visibleLocator(page, 'button').filter({ hasText: 'MOVIL DEMO' }).first()
  if (await asignacionBtn.count()) {
    await asignacionBtn.click()
    await page.waitForTimeout(300)
  } else {
    const search = visibleLocator(page, 'input[type="text"]').first()
    if (await search.count()) {
      await search.fill('MOVIL DEMO')
      await page.waitForTimeout(300)
      const item = page.locator('[data-moviles-item]:visible').first()
      if (await item.count()) await item.click({ force: true })
    }
  }
  await capture(page, '03-parte-equipo.png')

  await next(page)
  if (await visibleLocator(page, 'input[role="combobox"]').count()) {
    await choose(page, 'Tipo de Proceso', 'CAMIONETA DEMO')
  }
  await capture(page, '04-parte-proceso.png')

  // Sin horometro: el siguiente paso es Produccion (no hay "Tiempo").
  await next(page)
  await capture(page, '05-parte-produccion-sin-campos.png')

  await next(page)
  await page.getByRole('switch', { name: '¿Se cargó combustible?' }).click()
  await page.waitForTimeout(300)
  await fillField(page, 'Litros de gasoil', '45')
  await fillField(page, 'KM / Horómetro al cargar', '125000')
  await fillField(page, 'Remito 1', '000100009900')
  await capture(page, '06-parte-combustible.png')

  await next(page)
  if (await visibleLocator(page, 'label').filter({ hasText: 'Lugar de Carga' }).count()) {
    await choose(page, 'Lugar de Carga', 'LUGAR CARGA DEMO 01')
  }
  const observation = visibleLocator(page, 'textarea').first()
  if (await observation.count()) await observation.fill('Camioneta: carga de combustible y KM')
  await capture(page, '07-parte-ubicacion.png')

  await next(page)
  await capture(page, '08-parte-revision.png')

  await page.getByRole('button', { name: 'Guardar Registro', exact: true }).click()
  await page.waitForTimeout(700)
  await capture(page, '09-parte-guardado.png', { fullPage: false })

  await context.close()
}

async function captureListado(browser) {
  const context = await browser.newContext({ viewport, locale: 'es-AR', colorScheme: 'dark' })
  await seedSession(context, OPERADOR_USER)
  const page = await context.newPage()
  await page.route('**/api/**', (route) => mockApi(route))
  await page.goto(`${baseUrl}/mis-registros`)
  await waitForApp(page)
  await page.waitForTimeout(900)
  await capture(page, '10-mis-registros.png')
  await context.close()
}

async function captureAdmin(browser) {
  const context = await browser.newContext({ viewport, locale: 'es-AR', colorScheme: 'dark' })
  await seedSession(context, ADMIN_USER)
  const page = await context.newPage()
  await page.route('**/api/**', (route) => mockApi(route))

  await page.goto(`${baseUrl}/admin/crud/tipos-proceso`)
  await waitForApp(page)
  await page.waitForTimeout(900)
  await capture(page, '11-admin-tipos-lista.png')

  const nuevo = page.getByRole('button', { name: 'Nuevo', exact: true }).first()
  if (await nuevo.count()) {
    await nuevo.click()
    await page.waitForTimeout(500)
    const nameInput = visibleLocator(page, 'input').first()
    if (await nameInput.count()) await nameInput.fill('CAMIONETA')
    await capture(page, '12-admin-tipo-principal.png')

    const requisitos = page.getByRole('button', { name: 'Requisitos', exact: true }).first()
    if (await requisitos.count()) {
      await requisitos.click()
      await page.waitForTimeout(400)
      const horometro = page.locator('#requiere_horometro')
      if (await horometro.count()) await horometro.uncheck({ force: true }).catch(() => {})
      await capture(page, '13-admin-tipo-requisitos.png')
    }
  }
  await context.close()
}

async function startVite() {
  if (process.env.CAMIONETA_CAPTURE_BASE_URL) return null
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
  console.log(`[camioneta] iniciando en ${baseUrl}`)
  const vite = await startVite()
  const browser = await chromium.launch({ headless: true })
  try {
    await captureOperador(browser)
    await captureListado(browser)
    await captureAdmin(browser)
  } finally {
    await browser.close()
    if (vite) vite.kill()
  }
  const required = [
    '01-parte-contexto.png', '02-parte-operador.png', '03-parte-equipo.png',
    '04-parte-proceso.png', '05-parte-produccion-sin-campos.png',
    '06-parte-combustible.png', '07-parte-ubicacion.png', '08-parte-revision.png',
    '09-parte-guardado.png', '10-mis-registros.png', '13-admin-tipo-requisitos.png',
  ]
  const missing = required.filter((name) => !existsSync(join(outputRoot, name)))
  if (missing.length) throw new Error(`Faltan capturas: ${missing.join(', ')}`)
  console.log(`[camioneta] capturas en ${outputRoot}`)
}

main().catch((error) => {
  console.error(`[camioneta] ${error.message}`)
  process.exitCode = 1
})
