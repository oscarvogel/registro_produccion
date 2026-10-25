// Captura de la verificacion de evidencia por el encargado (issue #204).
//
// Genera las capturas reales de:
//   - el listado del dashboard con el filtro de evidencia y las marcas
//     "Observado" / "Sin verificar",
//   - el detalle del registro con la seccion de evidencia (foto, aviso de la
//     declaracion D7 y botones Verificar/Rechazar),
//   - el pedido de motivo al rechazar.
//
// La API esta mockeada (no hace falta MySQL ni backend). El script falla si
// la seccion no aparece o si los botones no estan.
//
// Uso:  node scripts/evidenciaVerificacionCapture.mjs
// Salida: docs/screenshots/evidencia_verificacion/*.png

import { existsSync, mkdirSync, readFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { spawn } from 'node:child_process'
import { setTimeout as sleep } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const frontendDir = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repoDir = resolve(frontendDir, '..')
const outputRoot = process.env.EVIDENCIA_VERIF_CAPTURE_OUT
  ? resolve(process.env.EVIDENCIA_VERIF_CAPTURE_OUT)
  : join(repoDir, 'docs', 'screenshots', 'evidencia_verificacion')
const host = '127.0.0.1'
const port = Number(process.env.EVIDENCIA_VERIF_CAPTURE_PORT || 4192)
const baseUrl = process.env.EVIDENCIA_VERIF_CAPTURE_BASE_URL || `http://${host}:${port}`

const VIEWPORTS = [
  { nombre: '1638x969', width: 1638, height: 969 },
  { nombre: '1366x768', width: 1366, height: 768 },
]

// Foto real para mostrar como evidencia (misma que usa el smoke offline).
const FOTO = join(
  repoDir,
  'docs',
  'screenshots',
  'evidencia_admin',
  '01-admin-tipos-lista-1638x969.png',
)

const UNIDAD = {
  idUnidadNegocio: 900001,
  nombre: 'Unidad Negocio Demo Forestal',
  prefijo: 'DEM',
  codigo_kobo: 'demo',
  activo: 1,
}

const ENCARGADO = {
  idPersonal: 900002,
  nombre: 'Encargado Demo',
  username: 'encargado',
  encargado: 1,
  is_admin: 0,
  unidad_negocio: 900001,
  unidad_ids: [900001],
}

const EVIDENCIAS = [
  {
    id: 77,
    registro_id: 42,
    form_uuid: 'uuid-42',
    tipo: 'procesador',
    incluye_horometro: 1,
    estado: 0,
    mime: 'image/jpeg',
    tamano: 90616,
    subido_at: '2026-10-20T14:05:00',
    cargado_por: 'OPERADOR DEMO',
  },
  {
    id: 78,
    registro_id: 42,
    form_uuid: 'uuid-42',
    tipo: 'horometro',
    incluye_horometro: 0,
    estado: 1,
    mime: 'image/jpeg',
    tamano: 51230,
    subido_at: '2026-10-20T14:06:00',
    verificado_por: 'Encargado Demo',
    verificado_at: '2026-10-20T15:10:00',
  },
]

const REGISTROS = [
  {
    id: 42,
    UN: 'Unidad Negocio Demo Forestal',
    fecha: '2026-10-20',
    operacion: 'PROCESO',
    operador: 'Operador Demo 01',
    equipo: 'Tractor John Deere 265',
    tipo_proceso_id: 3,
    hr_inicio: 1200,
    hr_fin: 1850,
    m3: 12,
    plantas: 3,
    form_uuid: 'uuid-42',
    evidencias_total: 2,
    evidencias_pendientes: 1,
    evidencias_rechazadas: 0,
  },
  {
    id: 41,
    UN: 'Unidad Negocio Demo Forestal',
    fecha: '2026-10-19',
    operacion: 'VOLTEO',
    operador: 'Operador Demo 01',
    equipo: 'Tractor John Deere 265',
    tipo_proceso_id: 4,
    form_uuid: 'uuid-41',
    evidencias_total: 1,
    evidencias_pendientes: 0,
    evidencias_rechazadas: 1,
  },
  {
    id: 40,
    UN: 'Unidad Negocio Demo Forestal',
    fecha: '2026-10-18',
    operacion: 'HORAS MAQUINAS',
    operador: 'Operador Demo 02',
    equipo: 'Cosechadora Case',
    tipo_proceso_id: 5,
    form_uuid: 'uuid-40',
    evidencias_total: 0,
    evidencias_pendientes: 0,
    evidencias_rechazadas: 0,
  },
]

function jsonResponse(route, body, status = 200) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function makeToken() {
  const encode = (value) => Buffer.from(JSON.stringify(value)).toString('base64url')
  return `${encode({ alg: 'none', typ: 'JWT' })}.${encode({ exp: 4102444800, sub: 'encargado-demo' })}.demo`
}

async function mockApi(route, fotoBytes) {
  const request = route.request()
  const url = new URL(request.url())
  const path = url.pathname
  const method = request.method()

  if (path === '/api/produccion/unidades-negocio') return jsonResponse(route, [UNIDAD])
  if (path === '/api/dashboard/tipos-proceso-disponibles') {
    return jsonResponse(route, [{ id: 3, value: 'tipo:3', nombre: 'PROCESO' }])
  }
  if (path === '/api/dashboard/moviles-disponibles') {
    return jsonResponse(route, [{ idMovil: 1, patente: 'AB123CD', detalle: 'Tractor John Deere 265' }])
  }
  if (path === '/api/dashboard/registros' && method === 'GET') {
    const evidencia = url.searchParams.get('evidencia')
    let items = REGISTROS
    if (evidencia === 'pendiente') {
      items = items.filter((fila) => Number(fila.evidencias_pendientes) > 0)
    } else if (evidencia === 'rechazada') {
      items = items.filter((fila) => Number(fila.evidencias_rechazadas) > 0)
    } else if (evidencia === 'sin_evidencia') {
      items = items.filter((fila) => Number(fila.evidencias_total) === 0)
    }
    return jsonResponse(route, {
      items,
      total: items.length,
      page: 1,
      page_size: 20,
      total_pages: 1,
    })
  }
  if (path === '/api/dashboard/registros/42' && method === 'GET') {
    return jsonResponse(route, { ...REGISTROS[0], cliente: 'Cliente Demo' })
  }
  if (path === '/api/produccion/registros/42/evidencias' && method === 'GET') {
    return jsonResponse(route, EVIDENCIAS)
  }
  if (path.startsWith('/api/produccion/evidencias/') && path.endsWith('/archivo')) {
    return route.fulfill({ status: 200, contentType: 'image/jpeg', body: fotoBytes })
  }
  if (path.startsWith('/api/produccion/evidencias/') && method === 'PATCH') {
    const cuerpo = JSON.parse(request.postData() || '{}')
    const evidencia = EVIDENCIAS.find((fila) => fila.id === Number(path.split('/')[5]))
    return jsonResponse(route, {
      ...evidencia,
      estado: Number(cuerpo.estado),
      comentario: cuerpo.comentario || '',
      verificado_por: 'Encargado Demo',
      verificado_at: '2026-10-25T10:00:00',
    })
  }
  if (path === '/health') return jsonResponse(route, { status: 'ok', database: 'ok' })
  if (path === '/api/health') return jsonResponse(route, { status: 'ok', database: 'ok' })
  if (path.startsWith('/api/')) return jsonResponse(route, [])
  return route.continue()
}

async function capture(page, name) {
  mkdirSync(outputRoot, { recursive: true })
  await page.waitForTimeout(300)
  await page.evaluate(() => window.scrollTo(0, 0))
  const path = join(outputRoot, name)
  await page.screenshot({ path, fullPage: false })
  console.log(`[verificacion-capture] captura -> ${path}`)
  return path
}

/**
 * Detecta pixeles que se salen de la ventana (el layout se comprime).
 * Lo que esta dentro de un area con scroll (el cuerpo del modal) puede
 * salirse a proposito: no cuenta como desborde.
 */
async function desbordes(page) {
  return page.evaluate(() => {
    const limiteAncho = window.innerWidth
    const limiteAlto = window.innerHeight
    const scrolleable = (nodo) => {
      let padre = nodo.parentElement
      while (padre && padre !== document.body) {
        const estilo = getComputedStyle(padre)
        if (/(auto|scroll)/.test(`${estilo.overflowY} ${estilo.overflowX}`)) return true
        padre = padre.parentElement
      }
      return false
    }
    const culpables = []
    document.querySelectorAll('body *').forEach((nodo) => {
      const caja = nodo.getBoundingClientRect()
      if (caja.width === 0 || caja.height === 0) return
      if (caja.right <= limiteAncho + 1 && caja.bottom <= limiteAlto + 1) return
      if (scrolleable(nodo)) return
      culpables.push(`${nodo.tagName}.${String(nodo.className || '').slice(0, 40)}`)
    })
    return [...new Set(culpables)].slice(0, 6)
  })
}

async function startVite() {
  if (process.env.EVIDENCIA_VERIF_CAPTURE_BASE_URL) return null
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
      // Vite todavia no levanta
    }
    await sleep(250)
  }
  child.kill()
  throw new Error(`No se pudo levantar Vite en ${baseUrl}.`)
}

async function main() {
  if (!existsSync(FOTO)) throw new Error(`Falta la foto de prueba: ${FOTO}`)
  const fotoBytes = readFileSync(FOTO)
  console.log(`[verificacion-capture] iniciando en ${baseUrl}`)
  const vite = await startVite()
  const browser = await chromium.launch({ headless: true })
  const fallos = []
  const reporte = []

  try {
    for (const viewport of VIEWPORTS) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        locale: 'es-AR',
        colorScheme: 'dark',
        serviceWorkers: 'block',
      })
      await context.addInitScript((payload) => {
        localStorage.setItem('token', payload.token)
        localStorage.setItem('user', JSON.stringify(payload.user))
        localStorage.setItem('catalogos_sync_ok', '1')
      }, { token: makeToken(), user: ENCARGADO })

      const page = await context.newPage()
      page.on('pageerror', (error) => console.error(`[verificacion-capture] error: ${error.message}`))
      await page.route('**/api/**', (route) => mockApi(route, fotoBytes))
      await page.route('**/health', (route) => mockApi(route, fotoBytes))

      // 1. Listado con el filtro de evidencia y las marcas.
      await page.goto(`${baseUrl}/dashboard/registros?un_id=900001`)
      await page.waitForLoadState('domcontentloaded')
      await page.waitForTimeout(2000)

      const filtro = page.locator('[data-testid="filtro-evidencia"]')
      if (!(await filtro.count())) {
        fallos.push(`${viewport.nombre}: no aparece el filtro de evidencia`)
      }
      const observados = await page.locator('[data-testid^="observado-"]').count()
      const sinVerificar = await page.locator('[data-testid^="sin-verificar-"]').count()
      if (observados < 1) fallos.push(`${viewport.nombre}: no se marca el registro con foto rechazada`)
      if (sinVerificar < 1) fallos.push(`${viewport.nombre}: no se marca el registro con foto sin verificar`)
      reporte.push(
        `${viewport.nombre}: listado -> observados ${observados}, sin verificar ${sinVerificar}`,
      )
      await capture(page, `01-listado-filtro-${viewport.nombre}.png`)

      // 2. Filtro "esperando verificación".
      await page.locator('[data-testid="filtro-evidencia-pendiente"]').click()
      await page.waitForTimeout(1500)
      const textoListado = await page.evaluate(() => document.body.innerText)
      if (!/sin verificar/i.test(textoListado)) {
        fallos.push(`${viewport.nombre}: el filtro "esperando verificación" no deja solo los pendientes`)
      }
      await capture(page, `02-filtro-pendientes-${viewport.nombre}.png`)
      reporte.push(`${viewport.nombre}: filtro "Esperando verificación" aplicado`)

      // 3. Detalle del registro con la seccion de evidencia.
      await page.locator('[data-testid="filtro-evidencia-todas"]').click()
      await page.waitForTimeout(1200)
      const verDetalle = page.getByRole('button', { name: /Ver detalle/ }).first()
      await verDetalle.click()
      await page.waitForTimeout(2000)

      const seccion = page.locator('[data-testid="record-detail-evidencia"]')
      if (!(await seccion.count())) {
        fallos.push(`${viewport.nombre}: el detalle no muestra la seccion de evidencia`)
      } else {
        if (!(await page.locator('[data-testid="evidencia-declaracion"]').count())) {
          fallos.push(`${viewport.nombre}: no aparece el aviso de la declaracion D7`)
        }
        if (!(await page.locator('[data-testid="evidencia-foto"]').count())) {
          fallos.push(`${viewport.nombre}: no se muestra la foto de evidencia`)
        }
        if (!(await page.locator('[data-testid="verificar-77"]').count())) {
          fallos.push(`${viewport.nombre}: el encargado no ve el boton Verificar`)
        }
        if (!(await page.locator('[data-testid="rechazar-77"]').count())) {
          fallos.push(`${viewport.nombre}: el encargado no ve el boton Rechazar`)
        }
      }
      await capture(page, `03-detalle-evidencia-${viewport.nombre}.png`)
      reporte.push(`${viewport.nombre}: detalle con la seccion de evidencia`)

      const desbordesModal = await desbordes(page)
      if (desbordesModal.length) {
        fallos.push(`${viewport.nombre}: el modal se desborda (${desbordesModal.join(', ')})`)
      }

      // 4. El rechazo pide el motivo.
      const rechazar = page.locator('[data-testid="rechazar-77"]')
      if (await rechazar.count()) {
        await rechazar.click()
        await page.waitForTimeout(900)
        const textoSwal = await page.evaluate(() => document.body.innerText)
        if (!textoSwal.includes('Rechazar la foto')) {
          fallos.push(`${viewport.nombre}: el rechazo no pide el motivo`)
        }
        await capture(page, `04-rechazar-motivo-${viewport.nombre}.png`)
        reporte.push(`${viewport.nombre}: el rechazo pide el motivo`)
        // Se cierra el dialogo para no dejar la pantalla sucia.
        const cancelar = page.getByRole('button', { name: /Cancelar/ })
        if (await cancelar.count()) {
          await cancelar.click()
          await page.waitForTimeout(500)
        }
      }

      await context.close()
    }

    console.log('---- RESULTADO ----')
    for (const linea of reporte) console.log(linea)
    if (fallos.length) {
      console.error('---- FALLOS ----')
      for (const linea of fallos) console.error(linea)
      process.exitCode = 1
    } else {
      console.log('---- SIN FALLOS ----')
    }
  } finally {
    await browser.close()
    if (vite) vite.kill()
  }
}

main().catch((error) => {
  console.error(`[verificacion-capture] ${error.message}`)
  process.exitCode = 1
})
