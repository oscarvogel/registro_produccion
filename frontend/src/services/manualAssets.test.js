import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync, statSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const frontendDir = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const manualsDir = resolve(frontendDir, 'public/manuales')
const repoDir = resolve(frontendDir, '..')
const capturesDir = resolve(repoDir, 'docs/manuales/capturas')
const roles = ['operador', 'encargado', 'admin']
const manualNames = roles.map((role) => `manual-${role}`)

const requiredCaptures = [
  '01-login.png',
  '02-sincronizar.png',
  '03-inicio.png',
  '04-menu-movil.png',
  '05-contexto.png',
  '06-operador.png',
  '07-equipo.png',
  '08-proceso.png',
  '09-tiempo.png',
  '10-produccion.png',
  '11-consumos.png',
  '12-ubicacion.png',
  '13-revision.png',
  '14-pendientes.png',
]

describe('manuales publicados', () => {
  it('incluye los tres Markdown y los tres PDF', () => {
    for (const name of manualNames) {
      expect(existsSync(resolve(manualsDir, `${name}.md`)), `${name}.md`).toBe(true)
      const pdf = resolve(manualsDir, 'pdf', `${name}.pdf`)
      expect(existsSync(pdf), `${name}.pdf`).toBe(true)
      expect(statSync(pdf).size, `${name}.pdf no debe estar vacío`).toBeGreaterThan(1024)
    }
  })

  it('apunta las imágenes de Markdown a archivos locales existentes', () => {
    for (const name of manualNames) {
      const markdown = readFileSync(resolve(manualsDir, `${name}.md`), 'utf8')
      const sources = [...markdown.matchAll(/!\[[^\]]*\]\((\/[^)]+)\)/g)].map((match) => match[1])
      for (const source of sources) {
        expect(source.startsWith('/manuales/'), `${name}: ${source}`).toBe(true)
        expect(existsSync(resolve(frontendDir, 'public', source.slice(1))), `${name}: ${source}`).toBe(true)
      }
    }
  })

  it('tiene las capturas móviles obligatorias para los tres roles', () => {
    for (const role of roles) {
      for (const capture of requiredCaptures) {
        const path = resolve(capturesDir, role, capture)
        expect(existsSync(path), `${role}/${capture}`).toBe(true)
        expect(statSync(path).size, `${role}/${capture} no debe estar vacío`).toBeGreaterThan(1024)
      }
    }
  })

  it('mantiene válidas las rutas PDF declaradas por ManualesView', () => {
    const view = readFileSync(resolve(frontendDir, 'src/views/ManualesView.vue'), 'utf8')
    for (const name of manualNames) {
      expect(view).toContain(`/manuales/pdf/${name}.pdf`)
    }
  })
})
