// Captura visual del paso "Evidencia" del formulario de produccion
// (issue #200).
//
// Usa la API mockeada y Vite, igual que scripts/evidenciaAdminCapture.mjs,
// para generar screenshots reales sin base de datos.
//
//   node scripts/evidenciaFormCapture.mjs
//
// Salida: docs/screenshots/evidencia_form/

import { existsSync, mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { spawn } from 'node:child_process'
import { setTimeout as sleep } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const frontendDir = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repoDir = resolve(frontendDir, '..')
const outputRoot = process.env.EVIDENCIA_FORM_CAPTURE_OUT
  ? resolve(process.env.EVIDENCIA_FORM_CAPTURE_OUT)
  : join(repoDir, 'docs', 'screenshots', 'evidencia_form')
const host = '127.0.0.1'
const port = Number(process.env.EVIDENCIA_FORM_CAPTURE_PORT || 4178)
const baseUrl = process.env.EVIDENCIA_FORM_CAPTURE_BASE_URL || `http://${host}:${port}`

// Viewports que usa el cliente (ver seccion 11 de AGENTS.md).
const VIEWPORTS = [
  { key: '1638x969', width: 1638, height: 969 },
  { key: '1366x768', width: 1366, height: 768 },
  { key: '390x844', width: 390, height: 844 },
]

// Foto real para cargar en el campo (el mismo screenshot del admin).
const FOTO = join(repoDir, 'docs', 'screenshots', 'evidencia_admin', '01-admin-tipos-lista-1638x969.png')

// Configuracion inicial de la decision D8: PROCESO exige foto del
// horometro y de la pantalla del procesador.
const TIPOS_PROCESO = [
  {
    id: 3,
    nombre: 'PROCESO',
    campos: 'm3,plantas',
    requiere_acta: false,
    requiere_predio: false,
    requiere_rodal: false,
    requiere_horometro: true,
    requiere_foto_horometro: true,
    requiere_foto_procesador: true,
    activo: 1,
  },
  {
    id: 1,
    nombre: 'CARGA',
    campos: 'tn_despachadas',
    requiere_acta: false,
    requiere_predio: false,
    requiere_rodal: false,
    requiere_horometro: true,
    requiere_foto_horometro: false,
    requiere_foto_procesador: false,
    activo: 1,
  },
]

const UNIDADES = [
  {
    idUnidadNegocio: 900001,
    nombre: 'Unidad Negocio Demo Forestal',
    prefijo: 'DEM',
    codigo_kobo: 'demo',
    activo: 1,
  },
]

const OPERADORES = [
  { idPersonal: 900011, nombre: 'Operador Demo 01', activo: 1, unidad_negocio: 900001 },
]

const ASIGNACIONES = [
  {
    idAsignacion: 1,
    idMovil: 1,
    idProceso: 3,
    detalle: 'Tractor John Deere 265',
    patente: 'AB123CD',
  },
]

const MOVILES = [
  { idMovil: 1, patente: 'AB123CD', detalle: 'Tractor John Deere 265', idChofer: 900011 },
]

const OPERADOR = {
  idPersonal: 900011,
  nombre: 'Operador Demo 01',
  username: 'operador',
  encargado: 0,
  is_admin: 0,
  unidad_negocio: 900001,
  unidad_ids: [900001],
}

function jsonResponse(route, body, status = 200) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function makeToken() {
  const encode = (value) => Buffer.from(JSON.stringify(value)).toString('base64url')
  return `${encode({ alg: 'none', typ: 'JWT' })}.${encode({ exp: 4102444800, sub: 'operador-demo' })}.demo`
}

async function mockApi(route) {
  const request = route.request()
  const path = new URL(request.url()).pathname
  const method = request.method()

  if (path === '/api/auth/login' && method === 'POST') {
    return jsonResponse(route, { access_token: makeToken(), user: OPERADOR })
  }
  // El sondeo de salud va a /health (no a /api/health) y exige status y
  // database en "ok": si no, la app muestra "Servidor no disponible".
  if (path === '/health') return jsonResponse(route, { status: 'ok', database: 'ok' })
  if (path === '/api/health') return jsonResponse(route, { status: 'ok', database: 'ok' })
  if (path === '/api/produccion/unidades-negocio') return jsonResponse(route, UNIDADES)
  if (path === '/api/produccion/tipo-proceso') return jsonResponse(route, TIPOS_PROCESO)
  if (path === '/api/produccion/tipos-proceso-all') return jsonResponse(route, TIPOS_PROCESO)
  if (path === '/api/produccion/operadores') return jsonResponse(route, OPERADORES)
  if (path === '/api/produccion/moviles') return jsonResponse(route, MOVILES)
  if (path.startsWith('/api/produccion/asignaciones/')) return jsonResponse(route, ASIGNACIONES)
  if (path.startsWith('/api/produccion/movil-by-operador/')) return jsonResponse(route, MOVILES[0])
  if (path === '/api/produccion/ultima-hora-fin') return jsonResponse(route, { hr_fin: 0 })
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

async function capture(page, name, { fullPage = true } = {}) {
  mkdirSync(outputRoot, { recursive: true })
  await page.waitForTimeout(250)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: join(outputRoot, name), fullPage })
}

// ─── helpers de interaccion ───
async function elegirAutocomplete(page, texto) {
  const combo = page.locator('input[role="combobox"]:visible').first()
  if (!(await combo.count())) {
    // Ya viene seleccionado (la app aplica la UN inicial sola).
    console.log(`[evidencia-form] "${texto}" ya viene seleccionado`)
    return
  }
  await combo.click()
  await combo.fill(texto)
  await page.waitForTimeout(350)
  const opcion = page.locator('[role="option"]:visible').first()
  await opcion.click()
  await page.waitForTimeout(500)
}

async function llenar(page, label, valor) {
  const input = page
    .locator(`label:has-text("${label}")`)
    .locator('xpath=..')
    .locator('input')
    .first()
  await input.fill(String(valor))
  await page.waitForTimeout(150)
}

async function siguiente(page) {
  const botones = page.getByRole('button', { name: 'Siguiente', exact: true })
  const total = await botones.count()
  for (let i = 0; i < total; i += 1) {
    if (await botones.nth(i).isVisible()) {
      await botones.nth(i).click()
      await page.waitForTimeout(500)
      return
    }
  }
  throw new Error('No se encontro el boton Siguiente visible')
}

// Mide el desborde horizontal: en 1366px la pantalla del cliente no puede
// quedar con contenido cortado (ver seccion 11 de AGENTS.md).
async function measureOverflow(page) {
  return page.evaluate(() => {
    const root = document.querySelector('.content-narrow')
    return {
      visible: root ? root.clientWidth : 0,
      needed: root ? root.scrollWidth : 0,
      overflow: root ? Math.max(0, root.scrollWidth - root.clientWidth) : 0,
      docOverflow: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
    }
  })
}

async function captureEvidencia(browser, viewport) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    locale: 'es-AR',
    colorScheme: 'dark',
    // El service worker de la PWA intercepta /api/... y esquiva el mock.
    serviceWorkers: 'block',
  })
  await seedSession(context, OPERADOR)
  const page = await context.newPage()
  page.on('pageerror', (error) => console.error(`[evidencia-form] error de pagina: ${error.message}`))
  await page.route('**/api/**', (route) => mockApi(route))
  // El sondeo de salud NO va por /api: es un fetch plano a /health.
  await page.route('**/health', (route) => {
    console.log(`[evidencia-form] health ${route.request().url()}`)
    return jsonResponse(route, { status: 'ok', database: 'ok' })
  })

  await page.goto(`${baseUrl}/produccion`)
  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(1200)

  // 1. Contexto: unidad de negocio
  await elegirAutocomplete(page, 'Demo Forestal')
  await siguiente(page)

  // 2. Operador: viene precargado (el operador no puede cambiarlo)
  await siguiente(page)

  // 3. Equipo: la asignacion del operador (o la maquina que ya viene)
  const asignacion = page.getByRole('button', { name: /Tractor John Deere 265/ }).first()
  if (await asignacion.count()) {
    await asignacion.click()
    await page.waitForTimeout(400)
  }
  await siguiente(page)

  // 4. Proceso
  await elegirAutocomplete(page, 'PROCESO')
  await siguiente(page)

  // 5. Tiempo
  await llenar(page, 'Horómetro inicial', 1200)
  await llenar(page, 'Horómetro final', 1850)
  await siguiente(page)

  // 6. Produccion
  await llenar(page, 'M³ (metros cúbicos)', 12)
  await llenar(page, 'Plantas', 3)
  await siguiente(page)

  const titulo = await page.locator('h3:visible').first().innerText()
  if (!titulo.toUpperCase().includes('EVIDENCIA')) {
    throw new Error(`No se llego al paso de evidencia (titulo visible: "${titulo}")`)
  }

  const medidas = await measureOverflow(page)
  console.log(
    `[evidencia-form] ${viewport.key}: desborde=${medidas.overflow}px doc=${medidas.docOverflow}px`,
  )
  const estado = await page.evaluate(() => (
    document.body.innerText.match(/Servidor (no )?disponible|Sin conexión|Verificando servidor/)?.[0] || 'sin etiqueta'
  ))
  console.log(`[evidencia-form] ${viewport.key}: conectividad="${estado}"`)

  await capture(page, `01-evidencia-paso-${viewport.key}.png`)

  // Foto real cargada en el campo del procesador
  const input = page.locator('input[type="file"]:visible, input[type="file"]').first()
  await input.setInputFiles(FOTO)
  await page.waitForTimeout(1200)
  await capture(page, `02-evidencia-con-foto-${viewport.key}.png`)

  // Declaracion del operador (D7): con el horometro en la misma pantalla
  const casilla = page.locator('input[type="checkbox"]:visible').first()
  await casilla.check()
  await page.waitForTimeout(500)
  await capture(page, `03-evidencia-declaracion-${viewport.key}.png`)

  await context.close()
}

async function startVite() {
  if (process.env.EVIDENCIA_FORM_CAPTURE_BASE_URL) return null
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
  if (!existsSync(FOTO)) throw new Error(`Falta la foto de prueba: ${FOTO}`)
  console.log(`[evidencia-form] iniciando en ${baseUrl}`)
  const vite = await startVite()
  const browser = await chromium.launch({ headless: true })
  try {
    for (const viewport of VIEWPORTS) {
      await captureEvidencia(browser, viewport)
    }
  } finally {
    await browser.close()
    if (vite) vite.kill()
  }

  const required = VIEWPORTS.flatMap((viewport) => [
    `01-evidencia-paso-${viewport.key}.png`,
    `02-evidencia-con-foto-${viewport.key}.png`,
    `03-evidencia-declaracion-${viewport.key}.png`,
  ])
  const missing = required.filter((name) => !existsSync(join(outputRoot, name)))
  if (missing.length) throw new Error(`Faltan capturas: ${missing.join(', ')}`)
  console.log(`[evidencia-form] capturas en ${outputRoot}`)
}

main().catch((error) => {
  console.error(`[evidencia-form] ${error.message}`)
  process.exitCode = 1
})
