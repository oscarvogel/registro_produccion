import { copyFileSync, existsSync, mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { spawn } from 'node:child_process'
import { setTimeout as sleep } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const frontendDir = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repoDir = resolve(frontendDir, '..')
const outputRoot = join(repoDir, 'docs', 'manuales', 'capturas')
const publicOutputRoot = join(frontendDir, 'public', 'manuales', 'capturas')
const host = '127.0.0.1'
const port = Number(process.env.DOCS_CAPTURE_PORT || 4174)
const mode = (process.env.DOCS_CAPTURE_MODE || 'mock').toLowerCase()
const baseUrl = process.env.DOCS_CAPTURE_BASE_URL || `http://${host}:${port}`
const viewport = { width: 390, height: 844, deviceScaleFactor: 1 }

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

async function capture(page, role, name, { fullPage = true } = {}) {
  const targetDir = join(outputRoot, role)
  mkdirSync(targetDir, { recursive: true })
  await page.waitForTimeout(250)
  await page.evaluate(() => window.scrollTo(0, 0))
  const outputPath = join(targetDir, name)
  await page.screenshot({ path: outputPath, fullPage })
  const publicDir = join(publicOutputRoot, role)
  mkdirSync(publicDir, { recursive: true })
  copyFileSync(outputPath, join(publicDir, name))
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

async function login(page, role) {
  const fixture = DEMO_USERS[role]
  await page.goto(`${baseUrl}/login`)
  await waitForApp(page)
  await capture(page, role, '01-login.png', { fullPage: false })
  await page.locator('button:visible').filter({ hasText: 'Sincronizar' }).first().click()
  await page.locator('span:visible').filter({ hasText: /Catálogos sincronizados/ }).first().waitFor()
  await capture(page, role, '02-sincronizar.png', { fullPage: false })
  await page.locator('#mobile-dni').fill(fixture.dni)
  await page.locator('#mobile-password').fill(fixture.password)
  await page.locator('button:visible').filter({ hasText: 'Ingresar' }).first().click()
  await page.waitForURL(`${baseUrl}/`)
  await waitForApp(page)
  await capture(page, role, '03-inicio.png')
  await page.getByRole('button', { name: 'Abrir navegacion' }).click()
  await page.getByRole('button', { name: 'Producción', exact: true }).click()
  await capture(page, role, '04-menu-movil.png', { fullPage: false })
  await page.getByRole('button', { name: 'Cerrar menu' }).click()
}

async function captureProduction(page, role) {
  await page.goto(`${baseUrl}/produccion`)
  await waitForApp(page)

  const contextUnit = visibleLocator(page, 'input[role="combobox"]').first()
  if (await contextUnit.count()) await choose(page, 'Unidad de Negocio', 'DEMO')
  await capture(page, role, '05-contexto.png')

  await next(page)
  const operatorField = visibleLocator(page, 'input[role="combobox"]')
  if (await operatorField.count()) await choose(page, 'Seleccionar Operador', 'OPERADOR DEMO')
  await capture(page, role, '06-operador.png')

  await next(page)
  await capture(page, role, '07-equipo.png')
  await next(page)
  if (await visibleLocator(page, 'input[role="combobox"]').count()) {
    await choose(page, 'Tipo de Proceso', 'PROCESO DEMO')
  }
  await capture(page, role, '08-proceso.png')

  await next(page)
  await fillField(page, 'Hora Inicio', '1350')
  await fillField(page, 'Hora Fin', '1382')
  await capture(page, role, '09-tiempo.png')

  await next(page)
  if (await visibleLocator(page, 'label').filter({ hasText: 'M³' }).count()) await fillField(page, 'M³', '24')
  if (await visibleLocator(page, 'label').filter({ hasText: 'TN Despachadas' }).count()) await fillField(page, 'TN Despachadas', '12.5')
  if (await visibleLocator(page, 'label').filter({ hasText: 'Horas a Disposición' }).count()) await fillField(page, 'Horas a Disposición', '7')
  await capture(page, role, '10-produccion.png')

  await next(page)
  const fuelLabel = page.getByText('¿Se cargó combustible?', { exact: true })
  await fuelLabel.locator('..').getByRole('button').click()
  await fillField(page, 'Litros de gasoil', '48')
  await fillField(page, 'KM / Horómetro al cargar', '1382')
  await fillField(page, 'Remito 1', '0001-00010001')
  await capture(page, role, '11-consumos.png')

  await next(page)
  await choose(page, 'Lugar de Carga', 'LUGAR DE CARGA DEMO')
  await choose(page, 'Acta', '1001')
  await choose(page, 'Predio', 'PREDIO DEMO')
  await choose(page, 'Rodal', 'R-01')
  const observation = visibleLocator(page, 'textarea').first()
  if (await observation.count()) await observation.fill('Registro ficticio para documentación')
  await capture(page, role, '12-ubicacion.png')

  await next(page)
  await capture(page, role, '13-revision.png')
}

async function captureRoleExtras(page, role) {
  await page.goto(`${baseUrl}/pendientes`)
  await waitForApp(page)
  await page.waitForTimeout(900)
  await capture(page, role, '14-pendientes.png')

  if (role === 'operador') {
    await page.goto(`${baseUrl}/mis-registros`)
    await waitForApp(page)
    await page.waitForTimeout(900)
    await capture(page, role, '15-mis-registros.png')
  } else if (role === 'encargado') {
    await page.goto(`${baseUrl}/dashboard`)
    await waitForApp(page)
    await page.waitForTimeout(2200)
    await capture(page, role, '15-dashboard-operativo.png')
  } else {
    await page.goto(`${baseUrl}/admin/gestion`)
    await waitForApp(page)
    await page.waitForTimeout(900)
    await capture(page, role, '15-admin-centro.png')
    await page.goto(`${baseUrl}/admin/dashboard`)
    await waitForApp(page)
    await page.waitForTimeout(2200)
    await capture(page, role, '16-admin-dashboard.png')
    await page.goto(`${baseUrl}/admin/configuracion`)
    await waitForApp(page)
    await page.waitForTimeout(900)
    await capture(page, role, '17-configuracion-acceso.png')
  }
}

async function startVite() {
  if (process.env.DOCS_CAPTURE_BASE_URL) return null
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
  throw new Error(`No se pudo levantar Vite en ${baseUrl}. Revisá Node.js y el puerto ${port}.`)
}

async function main() {
  if (mode === 'real' && (!process.env.DOCS_OPERADOR_DNI || !process.env.DOCS_OPERADOR_PASSWORD)) {
    throw new Error('DOCS_CAPTURE_MODE=real requiere DOCS_OPERADOR_DNI y DOCS_OPERADOR_PASSWORD; no se guardan en el repositorio.')
  }
  if (!['mock', 'real'].includes(mode)) throw new Error('DOCS_CAPTURE_MODE debe ser mock o real.')
  if (mode === 'real') throw new Error('El modo real requiere una sesión de prueba externa y aún no está habilitado por seguridad; usá DOCS_CAPTURE_MODE=mock.')

  console.log(`[docs:capture] iniciando en ${baseUrl} (${mode})`)
  const vite = await startVite()
  console.log('[docs:capture] Vite listo; iniciando Chromium')
  const browser = await chromium.launch({ headless: true })
  try {
    for (const role of selectedRoles) {
      console.log(`[docs:capture] capturando rol ${role}`)
      const context = await browser.newContext({
        viewport,
        locale: 'es-AR',
        colorScheme: 'light',
        serviceWorkers: 'block',
      })
      await context.addInitScript(() => {
        const installCaptureStyle = () => {
          const style = document.createElement('style')
          style.textContent = '* { animation-duration: 0s !important; transition-duration: 0s !important; scroll-behavior: auto !important; }'
          document.documentElement?.appendChild(style)
        }
        if (document.documentElement) installCaptureStyle()
        else document.addEventListener('DOMContentLoaded', installCaptureStyle, { once: true })
      })
      const page = await context.newPage()
      page.on('pageerror', (error) => console.error(`[docs:capture] error de página (${role}): ${error.message}`))
      await page.route('**/api/**', (route) => mockApi(route))
      await login(page, role)
      console.log(`[docs:capture] login listo: ${role}`)
      await captureProduction(page, role)
      console.log(`[docs:capture] producción lista: ${role}`)
      await captureRoleExtras(page, role)
      console.log(`[docs:capture] rol completo: ${role}`)
      await context.close()
    }
  } finally {
    await browser.close()
    if (vite) vite.kill()
  }

  const required = Object.keys(DEMO_USERS).flatMap((role) => [
    '01-login.png', '02-sincronizar.png', '03-inicio.png', '04-menu-movil.png',
    '05-contexto.png', '06-operador.png', '07-equipo.png', '08-proceso.png',
    '09-tiempo.png', '10-produccion.png', '11-consumos.png', '12-ubicacion.png',
    '13-revision.png', '14-pendientes.png',
  ].map((name) => join(outputRoot, role, name)))
  const missing = required.filter((path) => !existsSync(path))
  if (missing.length) throw new Error(`Faltan ${missing.length} capturas obligatorias. Primera faltante: ${missing[0]}`)
  console.log(`Capturas generadas en ${outputRoot}`)
}

main().catch((error) => {
  console.error(`[docs:capture] ${error.message}`)
  process.exitCode = 1
})
