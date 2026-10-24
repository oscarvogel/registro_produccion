// Smoke E2E del circuito offline de la evidencia (issue #202).
//
// Valida, contra la app real servida por Vite y con la API interceptada por
// un mock (sin MySQL ni backend de produccion), que:
//
//   1. El operador completa el wizard hasta el paso "Evidencia", toma la foto
//      y declara (D7) que el horometro se ve en esa pantalla.
//   2. SIN conexion, el registro NO se bloquea: la foto queda encolada en la
//      base local (IndexedDB) junto con el parte.
//   3. Al volver la conexion, el sync sube PRIMERO la foto y DESPUES el
//      parte, y el parte lleva los ids de la evidencia.
//   4. La cola queda vacia (el parte se borro) y la foto queda marcada como
//      subida.
//
// La API mockeada aborta los POST de produccion mientras la fase es
// "offline": si el formulario intentara subir algo sin conexion, el smoke
// falla en vez de dar un falso verde.
//
// Uso:  node scripts/evidenciaOfflineSmoke.mjs
// Salida: docs/screenshots/evidencia_offline/*.png

import { existsSync, mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { spawn } from 'node:child_process'
import { setTimeout as sleep } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const frontendDir = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repoDir = resolve(frontendDir, '..')
const outputRoot = process.env.EVIDENCIA_OFFLINE_SMOKE_OUT
  ? resolve(process.env.EVIDENCIA_OFFLINE_SMOKE_OUT)
  : join(repoDir, 'docs', 'screenshots', 'evidencia_offline')
const host = '127.0.0.1'
const port = Number(process.env.EVIDENCIA_OFFLINE_SMOKE_PORT || 4191)
const baseUrl = process.env.EVIDENCIA_OFFLINE_SMOKE_BASE_URL || `http://${host}:${port}`

const viewport = { width: 1638, height: 969 }

// Foto real para cargar en el campo (la misma que usa la captura del issue #200).
const FOTO = join(repoDir, 'docs', 'screenshots', 'evidencia_admin', '01-admin-tipos-lista-1638x969.png')

// Tipo de proceso con foto de procesador y de horometro (decision D8).
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
]

const UNIDADES = [
  { idUnidadNegocio: 900001, nombre: 'Unidad Negocio Demo Forestal', prefijo: 'DEM', codigo_kobo: 'demo', activo: 1 },
]

const OPERADORES = [
  { idPersonal: 900011, nombre: 'Operador Demo 01', activo: 1, unidad_negocio: 900001 },
]

const ASIGNACIONES = [
  { idAsignacion: 1, idMovil: 1, idProceso: 3, detalle: 'Tractor John Deere 265', patente: 'AB123CD' },
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

// Llamadas relevantes: las unicas dos que mandan la foto y el parte.
const llamadas = []
// 'online' | 'offline'
let fase = 'online'

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

  const esSubidaEvidencia = path === '/api/produccion/evidencias' && method === 'POST'
  const esParte = path === '/api/produccion/' && method === 'POST'

  if (esSubidaEvidencia || esParte) {
    // Sin conexion la app NO tiene que intentar nada: si lo intenta, el
    // smoke lo detecta (la llamada queda registrada como abortada).
    if (fase === 'offline') {
      llamadas.push({ path, method, fase, abortada: true })
      return route.abort('internetdisconnected')
    }
    if (esSubidaEvidencia) {
      const cuerpo = request.postData() || ''
      llamadas.push({
        path,
        method,
        fase,
        id: 77,
        multipart: cuerpo.length,
        formUuid: (cuerpo.match(/name="form_uuid"\r\n\r\n([^\r]+)/) || [])[1] || null,
        tipo: (cuerpo.match(/name="tipo"\r\n\r\n([^\r]+)/) || [])[1] || null,
      })
      return jsonResponse(route, { id: 77, tipo: 'procesador', estado: 0 })
    }
    let payload = {}
    try {
      payload = JSON.parse(request.postData() || '{}')
    } catch {
      payload = {}
    }
    llamadas.push({ path, method, fase, payload })
    return jsonResponse(route, { id: 900, ...payload })
  }

  if (path === '/api/auth/login' && method === 'POST') {
    return jsonResponse(route, { access_token: makeToken(), user: OPERADOR })
  }
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

// Lee una tabla de la base local (IndexedDB) desde la pagina.
async function leerTabla(page, tabla) {
  return page.evaluate(async (nombre) => new Promise((resolve, reject) => {
    const request = indexedDB.open('produccion_offline')
    request.onerror = () => reject(request.error)
    request.onsuccess = () => {
      const database = request.result
      if (!database.objectStoreNames.contains(nombre)) {
        database.close()
        resolve([])
        return
      }
      const store = database.transaction(nombre, 'readonly').objectStore(nombre)
      const all = store.getAll()
      all.onerror = () => {
        database.close()
        reject(all.error)
      }
      all.onsuccess = () => {
        database.close()
        resolve(all.result.map((row) => ({
          ...row,
          blobBytes: row.blob ? row.blob.size : null,
          blob: undefined,
        })))
      }
    }
  }), tabla)
}

async function capture(page, name) {
  mkdirSync(outputRoot, { recursive: true })
  await page.waitForTimeout(250)
  await page.evaluate(() => window.scrollTo(0, 0))
  const path = join(outputRoot, name)
  await page.screenshot({ path, fullPage: false })
  console.log(`[offline-smoke] captura -> ${path}`)
  return path
}

// ─── helpers de interaccion (mismos que la captura del issue #200) ───
async function elegirAutocomplete(page, texto) {
  const combo = page.locator('input[role="combobox"]:visible').first()
  if (!(await combo.count())) return
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

async function startVite() {
  if (process.env.EVIDENCIA_OFFLINE_SMOKE_BASE_URL) return null
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
  console.log(`[offline-smoke] iniciando en ${baseUrl}`)
  const vite = await startVite()
  const browser = await chromium.launch({ headless: true })
  const report = []
  const fallos = []

  try {
    const context = await browser.newContext({
      viewport,
      locale: 'es-AR',
      colorScheme: 'dark',
      // El service worker de la PWA intercepta /api/... y esquiva el mock.
      serviceWorkers: 'block',
    })
    await seedSession(context, OPERADOR)
    const page = await context.newPage()
    page.on('pageerror', (error) => console.error(`[offline-smoke] error de pagina: ${error.message}`))
    await page.route('**/api/**', (route) => mockApi(route))
    await page.route('**/health', (route) => mockApi(route))

    // ─── 1. Wizard hasta el paso de evidencia ───
    await page.goto(`${baseUrl}/produccion`)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1200)

    await elegirAutocomplete(page, 'Demo Forestal')
    await siguiente(page)
    await siguiente(page)
    const asignacion = page.getByRole('button', { name: /Tractor John Deere 265/ }).first()
    if (await asignacion.count()) {
      await asignacion.click()
      await page.waitForTimeout(400)
    }
    await siguiente(page)
    await elegirAutocomplete(page, 'PROCESO')
    await siguiente(page)
    await llenar(page, 'Horómetro inicial', 1200)
    await llenar(page, 'Horómetro final', 1850)
    await siguiente(page)
    await llenar(page, 'M³ (metros cúbicos)', 12)
    await llenar(page, 'Plantas', 3)
    await siguiente(page)

    const titulo = await page.locator('h3:visible').first().innerText()
    if (!titulo.toUpperCase().includes('EVIDENCIA')) {
      throw new Error(`No se llego al paso de evidencia (titulo visible: "${titulo}")`)
    }

    const input = page.locator('input[type="file"]').first()
    await input.setInputFiles(FOTO)
    await page.waitForTimeout(1500)
    // Declaracion D7: con el horometro en la misma pantalla alcanza una foto.
    const casilla = page.locator('input[type="checkbox"]:visible').first()
    await casilla.check()
    await page.waitForTimeout(500)
    await capture(page, '01-evidencia-con-foto-1638x969.png')
    report.push('1. wizard completo hasta el paso Evidencia con la foto y la declaracion D7')

    // ─── 2. Aguantar OFFLINE y guardar ───
    // Vite sirve los .vue por HTTP: sin conexion el router no puede bajar
    // un chunk que todavia no cargo. Se precargan las pantallas que el
    // operador va a ver (inicio y pendientes) antes de cortar la red.
    await page.evaluate(async () => {
      await import('/src/views/HomeView.vue')
      await import('/src/views/PendientesView.vue')
    })

    fase = 'offline'
    await context.setOffline(true)
    await page.evaluate(() => {
      Object.defineProperty(window.navigator, 'onLine', { get: () => false, configurable: true })
      window.dispatchEvent(new Event('offline'))
    })
    await page.waitForTimeout(600)

    // Desde Evidencia todavia faltan Consumos, Ubicacion y Revision.
    for (let intento = 0; intento < 4; intento += 1) {
      if (await page.getByRole('button', { name: /Guardar Registro/ }).count()) break
      await siguiente(page)
      await page.waitForTimeout(500)
    }
    const paso = await page.evaluate(() => ({
      paso: (document.body.innerText.match(/Paso \d+ de \d+/) || [''])[0],
      botones: [...document.querySelectorAll('button')].map((b) => b.textContent.trim()).filter(Boolean),
    }))
    console.log(`[offline-smoke] paso tras "Siguiente": ${JSON.stringify(paso)}`)
    await capture(page, '01b-paso-revision-1638x969.png')

    const botonGuardar = page.getByRole('button', { name: /Guardar Registro/ }).first()
    await botonGuardar.click()

    await page.waitForSelector('text=Guardado solo en este teléfono', { timeout: 15000 })
    await capture(page, '02-guardado-sin-conexion-1638x969.png')
    report.push('2. sin conexion el registro se guardo en el telefono (Swal "Guardado solo en este telefono")')

    const botonEntendido = page.getByRole('button', { name: /Entendido/ }).first()
    if (await botonEntendido.count()) {
      await botonEntendido.click()
      await page.waitForTimeout(1200)
    }

    // ─── 3. La foto y el parte quedaron en la cola local ───
    const evidencias = await leerTabla(page, 'pendingEvidencias')
    const registros = await leerTabla(page, 'pendingRecords')
    report.push(
      `3. cola local -> evidencias: ${evidencias.length} (blob ${evidencias[0]?.blobBytes ?? 0} bytes, synced ${evidencias[0]?.synced}) | registros: ${registros.length}`,
    )
    if (evidencias.length !== 1) fallos.push(`la cola de evidencias tiene ${evidencias.length} filas (se esperaba 1)`)
    if (registros.length !== 1) fallos.push(`la cola de partes tiene ${registros.length} filas (se esperaba 1)`)
    if (!(evidencias[0]?.blobBytes > 0)) fallos.push('la foto encolada no tiene contenido')
    if (evidencias[0]?.synced !== 0) fallos.push('la foto encolada ya figura como subida')
    const mismoUuid = evidencias[0]?.formUuid && evidencias[0].formUuid === registros[0]?.payload?.form_uuid
    if (!mismoUuid) fallos.push('la foto y el parte no comparten el mismo form_uuid')

    const enviosSinConexion = llamadas.filter((llamada) => llamada.abortada)
    if (enviosSinConexion.length) {
      fallos.push(`se intentó enviar ${enviosSinConexion.length} cosa(s) sin conexión`)
    } else {
      report.push('4. sin conexion NO se intentó enviar ni la foto ni el parte')
    }

    // ─── 4. Pantalla de Pendientes: el operador ve que la foto espera ───
    // Navegacion con el router de la app (sin red no hay recarga de pagina).
    await page.evaluate(async () => {
      const { default: router } = await import('/src/router/index.js')
      await router.push('/pendientes')
    })
    await page.waitForTimeout(1800)
    const textoPendientes = await page.evaluate(() => document.body.innerText)
    const badge = textoPendientes.match(/\d+ foto\(s\) adjunta\(s\), esperando subir/)?.[0] || ''
    await capture(page, '03-pendientes-foto-en-espera-1638x969.png')
    report.push(`5. pantalla Pendientes -> badge: "${badge || '(no aparece)'}"`)
    if (!badge) fallos.push('la pantalla Pendientes no avisa que la foto sigue en el telefono')

    // ─── 5. Vuelve la conexion: el sync sube la foto y DESPUES el parte ───
    fase = 'online'
    await context.setOffline(false)
    await page.evaluate(() => {
      Object.defineProperty(window.navigator, 'onLine', { get: () => true, configurable: true })
      window.dispatchEvent(new Event('online'))
    })

    const limite = Date.now() + 30000
    while (Date.now() < limite) {
      if (llamadas.some((llamada) => llamada.path === '/api/produccion/' && !llamada.abortada)) break
      await page.waitForTimeout(500)
    }

    const subida = llamadas.find((llamada) => llamada.path === '/api/produccion/evidencias')
    const parte = llamadas.find((llamada) => llamada.path === '/api/produccion/')
    const orden = llamadas.map((llamada) => llamada.path)
    report.push(`6. orden de las llamadas -> ${orden.join(' -> ')}`)

    if (!subida) fallos.push('la foto no se subio al volver la conexion')
    if (!parte) fallos.push('el parte no se envio al volver la conexion')
    if (subida && parte && orden.indexOf('/api/produccion/evidencias') > orden.indexOf('/api/produccion/')) {
      fallos.push('el parte se envio ANTES que la foto')
    }
    if (subida && parte && orden.indexOf('/api/produccion/evidencias') < orden.indexOf('/api/produccion/')) {
      report.push('7. la foto se subio antes que el parte (orden correcto)')
    }
    const idsEvidencia = parte?.payload?.evidencias
    if (!parte || !Array.isArray(idsEvidencia) || idsEvidencia.length !== 1) {
      fallos.push(`el parte no lleva los ids de la evidencia (evidencias=${JSON.stringify(idsEvidencia)})`)
    } else {
      report.push(`8. el parte lleva evidencias=${JSON.stringify(idsEvidencia)} (id ${subida?.id ?? 'n/d'})`)
    }
    if (subida && subida.formUuid && parte && subida.formUuid !== parte.payload?.form_uuid) {
      fallos.push('la foto y el parte no comparten el form_uuid en el servidor')
    }

    await page.waitForTimeout(1500)
    const evidenciasFinal = await leerTabla(page, 'pendingEvidencias')
    const registrosFinal = await leerTabla(page, 'pendingRecords')
    report.push(
      `9. cola local tras sincronizar -> evidencias: ${evidenciasFinal.length} (synced ${evidenciasFinal[0]?.synced}) | registros: ${registrosFinal.length}`,
    )
    if (registrosFinal.length !== 0) fallos.push(`el parte sigue en la cola local (${registrosFinal.length} filas)`)
    if (evidenciasFinal[0]?.synced !== 1) fallos.push('la foto no quedo marcada como subida')

    await capture(page, '04-pendientes-tras-sincronizar-1638x969.png')

    console.log('---- RESULTADO ----')
    for (const line of report) console.log(line)
    if (fallos.length) {
      console.error('---- FALLOS ----')
      for (const line of fallos) console.error(line)
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
  console.error(`[offline-smoke] ${error.message}`)
  process.exitCode = 1
})
