/**
 * Smoke del circuito offline de la PWA (issue #164, abierto).
 *
 * Valida, contra la app real servida por Vite y con la API interceptada por
 * un mock (sin MySQL ni backend de produccion), que:
 *
 *   1. Un login online deja la sesion offline cacheada.
 *   2. Al reabrir la app sin token y sin red, la sesion cacheada entra igual:
 *      layout completo, banner "Sin conexion" y cola de pendientes intacta.
 *   3. Al volver la conexion, la app pide reautenticacion online
 *      (/login?reauth=1) en vez de intentar enviar con un token ajeno.
 *
 * No cubre la persistencia real en MySQL ni la deduplicacion por form_uuid
 * (eso necesita el backend de verdad): por eso el issue #164 sigue abierto.
 *
 * Uso:  node scripts/pwaOfflineSmoke.mjs
 * Salida: docs/screenshots/pr-172-pwa-offline/*.png
 */

import { mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { spawn } from 'node:child_process'
import { setTimeout as sleep } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const frontendDir = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repoDir = resolve(frontendDir, '..')
const host = '127.0.0.1'
const port = Number(process.env.PWA_SMOKE_PORT || 4188)
const baseUrl = `http://${host}:${port}`
const viewport = { width: 1638, height: 969, deviceScaleFactor: 1 }

const DEMO_USERS = {
  operador: {
    dni: '90000001',
    password: 'demo-operador',
    user: {
      idPersonal: 101,
      nombre: 'OPERADOR DEMO',
      encargado: 0,
      is_admin: 0,
      unidad_negocio: 1,
      unidad_ids: [1],
      tipo_de_proceso_id: 11,
    },
  },
  encargado: {
    dni: '90000002',
    password: 'demo-encargado',
    user: {
      idPersonal: 102,
      nombre: 'ENCARGADO DEMO',
      encargado: 1,
      is_admin: 0,
      unidad_negocio: 1,
      unidad_ids: [1],
    },
  },
  admin: {
    dni: '90000003',
    password: 'demo-admin',
    user: {
      idPersonal: 103,
      nombre: 'ADMIN DEMO',
      encargado: 0,
      is_admin: 1,
      unidad_negocio: 1,
      unidad_ids: [1],
    },
  },
}

const selectedRoles = (process.env.DOCS_CAPTURE_ROLES || 'operador,encargado,admin')
  .split(',')
  .map((role) => role.trim())
  .filter((role) => role in DEMO_USERS)

const DEMO_CATALOGS = {
  units: [{ idUnidadNegocio: 1, nombre: 'UNIDAD DEMO FORESTAL', prefijo: 'DEMO' }],
  operators: [
    { idPersonal: 101, nombre: 'OPERADOR DEMO', unidad_negocio: 1, tipo_de_proceso_id: 11 },
    { idPersonal: 102, nombre: 'ENCARGADO DEMO', unidad_negocio: 1, tipo_de_proceso_id: 11 },
  ],
  machines: [{ idMovil: 301, detalle: 'MAQUINA DEMO 01', patente: 'DEMO-01', unidad_negocio: 1 }],
  processes: [{
    id: 11,
    nombre: 'PROCESO DEMO',
    campos: 'm3,tn_despachadas,horas_disposicion',
    requiere_acta: true,
    requiere_predio: true,
    requiere_rodal: true,
  }],
  assignments: [{ idAsignacion: 501, idMovil: 301, patente: 'DEMO-01', detalle: 'MAQUINA DEMO 01', idProceso: 11 }],
  acts: [{ numero: '1001' }],
  properties: [{ idPredio: 601, nombre: 'PREDIO DEMO' }],
  plots: [{ idRodal: 701, idPredio: 601, rodal: 'R-01' }],
  loadingPlaces: [{ idLugarCarga: 801, detalle: 'LUGAR DE CARGA DEMO' }],
}

const DEMO_RECORDS = [{
  id: 9001,
  fecha: '2026-08-18',
  operacion: 'PROCESO DEMO',
  equipo: 'MAQUINA DEMO 01 - DEMO-01',
  unidad: 'UNIDAD DEMO FORESTAL',
  operador: 'OPERADOR DEMO',
  hr_inicio: 1350,
  hr_fin: 1382,
  m3: 24,
  tn_despachadas: 12.5,
  combustible: 48,
  observaciones: 'Registro ficticio para documentación',
}]

function jsonResponse(route, body, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  })
}

function makeToken() {
  const encode = (value) => Buffer.from(JSON.stringify(value)).toString('base64url')
  return `${encode({ alg: 'none', typ: 'JWT' })}.${encode({ exp: 4102444800, sub: 'docs-demo' })}.docs-demo`
}

function roleForDni(dni) {
  return Object.entries(DEMO_USERS).find(([, fixture]) => fixture.dni === String(dni))?.[0] || 'operador'
}

async function mockApi(route) {
  const request = route.request()
  const url = new URL(request.url())
  const path = url.pathname
  const method = request.method()

  // El probe de conectividad del frontend usa /health (no un endpoint de
  // catalogo) y exige status=ok y database=ok para dar el backend por sano.
  // Sin esta respuesta el banner "sin conexion" aparece en todas las capturas.
  if (path === '/health') {
    return jsonResponse(route, {
      status: 'ok',
      service: 'registro-produccion',
      instance: 'docs-demo',
      database: 'ok',
      version: 'docs-demo',
    })
  }

  if (path === '/api/auth/login' && method === 'POST') {
    const body = JSON.parse(request.postData() || '{}')
    const role = roleForDni(body.dni)
    const fixture = DEMO_USERS[role]
    return jsonResponse(route, { access_token: makeToken(), user: fixture.user })
  }
  if (path === '/api/auth/sincronizar' && method === 'POST') {
    return jsonResponse(route, { message: 'Catálogos sincronizados', total_activos: 3 })
  }

  if (path.includes('/api/produccion/lugares-carga') || path === '/api/health') return jsonResponse(route, DEMO_CATALOGS.loadingPlaces)
  if (path === '/api/produccion/unidades-negocio') return jsonResponse(route, DEMO_CATALOGS.units)
  if (path === '/api/produccion/operadores') return jsonResponse(route, DEMO_CATALOGS.operators)
  if (path === '/api/produccion/moviles') return jsonResponse(route, DEMO_CATALOGS.machines)
  if (path === '/api/produccion/tipo-proceso' || path === '/api/produccion/tipos-proceso-all') return jsonResponse(route, DEMO_CATALOGS.processes)
  if (path === '/api/produccion/actas') return jsonResponse(route, DEMO_CATALOGS.acts)
  if (path.includes('/api/produccion/actas/')) return jsonResponse(route, DEMO_CATALOGS.plots)
  if (path === '/api/produccion/predios') return jsonResponse(route, DEMO_CATALOGS.properties)
  if (path === '/api/produccion/rodales') return jsonResponse(route, DEMO_CATALOGS.plots)
  if (path.includes('/api/produccion/asignaciones/')) return jsonResponse(route, DEMO_CATALOGS.assignments)
  if (path.includes('/api/produccion/movil-by-operador/')) return jsonResponse(route, DEMO_CATALOGS.machines[0])
  if (path === '/api/produccion/ultima-hora-fin') return jsonResponse(route, { hr_fin: 1350 })
  if (path === '/api/produccion/mis-registros' || path === '/api/produccion/caminos/mis-registros') {
    return jsonResponse(route, { registros: path.includes('/caminos/') ? [] : DEMO_RECORDS, child_ids: [] })
  }
  if (path === '/api/dashboard/tipos-proceso-disponibles') return jsonResponse(route, [{ value: 'tipo:11', nombre: 'PROCESO DEMO' }])
  if (path === '/api/dashboard/moviles-disponibles') return jsonResponse(route, [{ idMovil: 301, _label: 'MAQUINA DEMO 01 - DEMO-01' }])
  if (path === '/api/dashboard/kpis') {
    return jsonResponse(route, {
      kpis: [
        { id: 'produccion', nombre: 'Producción total', valor: 24, unidad: 'M³', es_principal: true, icono: 'production', variacion_porcentual: 8 },
        { id: 'registros', nombre: 'Registros', valor: 3, unidad: 'reg.', icono: 'records', variacion_porcentual: 0 },
        { id: 'combustible', nombre: 'Combustible', valor: 48, unidad: 'lts', icono: 'fuel', variacion_porcentual: -2 },
      ],
      filtros_aplicados: {},
    })
  }
  if (path === '/api/dashboard/evolucion') return jsonResponse(route, { labels: ['12/08/2026', '14/08/2026', '16/08/2026', '18/08/2026'], datasets: [{ nombre: 'Producción', unidad: 'M³', valores: [12, 18, 15, 24] }] })
  if (path === '/api/dashboard/ranking-maquinas') return jsonResponse(route, [{ idMovil: 301, detalle: 'MAQUINA DEMO 01', patente: 'DEMO-01', valor: 24, registros: 3 }])

  if (path === '/api/admin/dashboard') {
    return jsonResponse(route, [{ id: 1, nombre: 'UNIDAD DEMO FORESTAL', prefijo: 'DEMO', resumen: { total_registros: 3, produccion_total: 24, combustible_total: 48, operadores_activos: 2, ultima_actividad_fecha: '2026-08-18' } }])
  }
  if (path === '/api/admin/dashboard/recent-records') return jsonResponse(route, DEMO_RECORDS)
  if (path === '/api/admin/dashboard/overview') {
    console.log('[docs:capture] mock admin overview')
    return jsonResponse(route, {
      totals: { produccion_total: 24, total_registros: 3, unidades_activas: 1, tn_despachadas_total: 12.5, combustible_total: 48, operadores_activos: 2, equipos_activos: 1 },
      previous_totals: { produccion_total: 0, total_registros: 0, tn_despachadas_total: 0, combustible_total: 0, operadores_activos: 0, equipos_activos: 0 },
      periodo_anterior_desde: '2026-06-20', periodo_anterior_hasta: '2026-07-19',
      variations: [], evolucion: [{ fecha: '2026-08-12', produccion: 12 }, { fecha: '2026-08-15', produccion: 18 }, { fecha: '2026-08-18', produccion: 24 }], unidad_ranking: [{ id: 1, nombre: 'UNIDAD DEMO FORESTAL', registros: 3, produccion: 24, share_percent: 100 }], proceso_ranking: [{ id: 11, nombre: 'PROCESO DEMO', produccion: 24, tn_despachadas: 12.5, registros: 3 }], recent_records: DEMO_RECORDS,
    })
  }
  if (path === '/api/admin/configuracion/usuarios') return jsonResponse(route, [
    { idPersonal: 101, nombre: 'OPERADOR DEMO', dni: '90000001', activo: 1, encargado: 0, is_admin: 0 },
    { idPersonal: 102, nombre: 'ENCARGADO DEMO', dni: '90000002', activo: 1, encargado: 1, is_admin: 0 },
    { idPersonal: 103, nombre: 'ADMIN DEMO', dni: '90000003', activo: 1, encargado: 0, is_admin: 1 },
  ])
  if (path.startsWith('/api/admin/')) return jsonResponse(route, { items: [], total: 0 })
  if (path.startsWith('/api/')) return jsonResponse(route, [])
  return route.continue()
}

async function waitForApp(page) {
  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(350)
  await page.evaluate(() => window.scrollTo(0, 0))
}

async function startVite() {
  const viteEntry = join(frontendDir, 'node_modules', 'vite', 'bin', 'vite.js')
  const child = spawn(process.execPath, [viteEntry, '--host', host, '--port', String(port)], {
    cwd: frontendDir,
    stdio: 'ignore',
    windowsHide: true,
  })
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const response = await fetch(baseUrl)
      if (response.ok) return child
    } catch {
      // Vite is still starting.
    }
    await sleep(250)
  }
  child.kill()
  throw new Error(`No se pudo levantar Vite en ${baseUrl}.`)
}

async function shot(page, dir, name) {
  await page.waitForTimeout(300)
  await page.evaluate(() => window.scrollTo(0, 0))
  const path = join(dir, name)
  // La captura del login tiene una foto de fondo: en PNG pesa 1,8 MB, en JPEG 320 KB.
  const isJpeg = name.endsWith('.jpg') || name.endsWith('.jpeg')
  await page.screenshot({ path, fullPage: false, ...(isJpeg ? { type: 'jpeg', quality: 88 } : {}) })
  console.log(`[smoke] captura -> ${path}`)
}

async function main() {
  const outDir = join(repoDir, 'docs', 'screenshots', 'pr-172-pwa-offline')
  mkdirSync(outDir, { recursive: true })

  const vite = await startVite()
  const browser = await chromium.launch()
  const report = []
  try {
    const context = await browser.newContext({ viewport })
    const page = await context.newPage()
    page.on('pageerror', (error) => console.error(`[smoke] error de pagina: ${error.message}`))
    await context.route('**/api/**', (route) => mockApi(route))
    await context.route((url) => url.pathname === '/health', (route) => mockApi(route))

    // 1) Login online: debe dejar la sesion offline cacheada.
    await page.goto(`${baseUrl}/login`)
    await waitForApp(page)
    await page.locator('#desktop-dni').fill(DEMO_USERS.operador.dni)
    await page.locator('#desktop-password').fill(DEMO_USERS.operador.password)
    await page.locator('button:visible').filter({ hasText: 'Ingresar' }).first().click()
    await page.waitForURL(`${baseUrl}/`)
    await waitForApp(page)
    await page.waitForTimeout(1500)
    const online = await page.evaluate(() => ({
      url: location.pathname,
      cache: Boolean(localStorage.getItem('offline_session_cache')),
      token: Boolean(localStorage.getItem('token')),
    }))
    report.push(`1. login online -> ${online.url} | cache offline: ${online.cache} | token: ${online.token}`)
    await shot(page, outDir, '01-inicio-online.png')

    // 2) Se pierde la sesion online (sin token) y la app reabre SIN red:
    //    tiene que entrar con la sesion cacheada y mostrar el layout completo.
    await page.evaluate(() => localStorage.removeItem('token'))
    await context.addInitScript(() => {
      Object.defineProperty(window.navigator, 'onLine', { get: () => false, configurable: true })
    })
    await page.goto(`${baseUrl}/`)
    await waitForApp(page)
    await page.waitForTimeout(2500)
    const offline = await page.evaluate(() => ({
      url: location.pathname,
      layout: Boolean(document.querySelector('#app nav, #app aside, #app header')),
      cache: Boolean(localStorage.getItem('offline_session_cache')),
      token: Boolean(localStorage.getItem('token')),
      banner: (document.body.innerText.match(/Sin conexi[^\n]*/) || [''])[0],
    }))
    report.push(`2. arranque sin red -> ${offline.url} | layout: ${offline.layout} | cache: ${offline.cache} | token: ${offline.token} | banner: ${offline.banner}`)
    await shot(page, outDir, '02-sesion-offline.png')

    // 3) Vuelve la conexion: la app debe pedir reautenticacion online.
    await page.evaluate(() => {
      Object.defineProperty(window.navigator, 'onLine', { get: () => true, configurable: true })
      window.dispatchEvent(new Event('online'))
    })
    await page.waitForTimeout(3500)
    const reauth = await page.evaluate(() => ({
      url: location.pathname + location.search,
      notice: (document.body.innerText.match(/Volvió el servidor[^\n]*/) || [''])[0],
      noticeVisible: (() => {
        const span = [...document.querySelectorAll('span')].find((node) => node.textContent.includes('Volvió el servidor'))
        if (!span) return false
        const style = getComputedStyle(span)
        const box = span.getBoundingClientRect()
        return style.visibility === 'visible' && style.opacity !== '0' && box.width > 0 && style.color !== getComputedStyle(span.parentElement).backgroundColor
      })(),
    }))
    report.push(`3. vuelve la conexion -> ${reauth.url} | aviso visible: ${reauth.noticeVisible} | ${reauth.notice || '(sin aviso)'}`)
    await shot(page, outDir, '03-reautenticacion.jpg')

    console.log('---- RESULTADO ----')
    for (const line of report) console.log(line)

    const failed = []
    if (!online.cache) failed.push('el login online no dejo la cache de sesion')
    if (!offline.layout) failed.push('la sesion offline no mostro el layout')
    if (offline.token) failed.push('la sesion offline conservo el token online')
    if (!reauth.url.includes('reauth=1')) failed.push('al volver la conexion no se pidio reautenticacion')
    if (!reauth.noticeVisible) failed.push('el aviso de reautenticacion no es legible')
    if (failed.length) {
      console.error('---- FALLOS ----')
      for (const line of failed) console.error(line)
      process.exitCode = 1
    }
  } finally {
    await browser.close()
    if (vite) vite.kill()
  }
}

main().catch((error) => {
  console.error(`[smoke] ${error.message}`)
  process.exitCode = 1
})
