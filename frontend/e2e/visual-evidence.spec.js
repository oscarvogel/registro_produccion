import { expect, test } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const currentDir = path.dirname(fileURLToPath(import.meta.url))
const versionedEvidenceDir = process.env.VISUAL_EVIDENCE_DIR
  ? path.resolve(currentDir, process.env.VISUAL_EVIDENCE_DIR)
  : null

const screenshotNames = {
  'desktop-chromium': {
    login: '01-login-desktop.png',
    admin: '02-admin-center-desktop.png',
    pending: '03-pending-desktop.png',
  },
  'mobile-chromium': {
    login: '04-login-mobile.png',
    admin: '05-admin-center-mobile.png',
    pending: '06-pending-mobile.png',
  },
}

function createTestToken() {
  const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url')
  const payload = Buffer.from(JSON.stringify({ exp: 4102444800 })).toString('base64url')
  return `${header}.${payload}.test`
}

async function mockBackend(page) {
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url())
    const body = url.pathname.endsWith('/health')
      ? { status: 'ok', database: 'ok' }
      : []
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(body),
    })
  })
}

async function setAdminSession(page) {
  const token = createTestToken()
  const user = {
    idPersonal: 1,
    DNI: '99999999',
    nombre: 'Administrador visual',
    is_admin: 1,
    encargado: 1,
    unidad_negocio: 1,
    unidad_ids: [1],
  }
  await page.addInitScript(
    ({ sessionToken, sessionUser }) => {
      localStorage.setItem('token', sessionToken)
      localStorage.setItem('user', JSON.stringify(sessionUser))
    },
    { sessionToken: token, sessionUser: user },
  )
}

test.beforeEach(async ({ page }) => {
  await mockBackend(page)
})

test('captures the current login, administration and pending-record flows', async ({ page }, testInfo) => {
  const names = screenshotNames[testInfo.project.name]
  const screenshotPath = (name) => versionedEvidenceDir
    ? path.join(versionedEvidenceDir, name)
    : testInfo.outputPath(name)

  await page.goto('/login')
  await expect(page.getByRole('heading', { name: 'Acceso operativo' })).toBeVisible()
  await page.screenshot({ path: screenshotPath(names.login), fullPage: true })

  await setAdminSession(page)
  await page.goto('/admin/gestion')
  await expect(page.getByRole('heading', { name: 'Centro administrativo' })).toBeVisible()
  if (testInfo.project.name === 'mobile-chromium') {
    await page.getByRole('button', { name: 'Abrir navegacion' }).click()
  }
  await expect(page.getByRole('link', { name: 'Administración' })).toBeVisible()
  await page.screenshot({ path: screenshotPath(names.admin), fullPage: true })

  await page.goto('/pendientes')
  await expect(page.getByRole('heading', { name: 'Registros Pendientes' })).toBeVisible()
  const emptyQueueMessage = page.getByText(
    'No hay registros pendientes ni fallidos para tu alcance actual.',
  )
  await expect(emptyQueueMessage).toBeVisible()
  await page.waitForTimeout(500)
  await page.screenshot({
    path: screenshotPath(names.pending),
    fullPage: testInfo.project.name !== 'mobile-chromium',
  })
})
