import { afterEach, describe, expect, it, vi } from 'vitest'

import { comprimirImagen } from './imagen'

function archivoFalso(nombre = 'foto.jpg', bytes = 2048) {
  return new File([new Uint8Array(bytes)], nombre, { type: 'image/jpeg' })
}

function mockCanvas(toBlob) {
  const drawImage = vi.fn()
  vi.spyOn(document, 'createElement').mockImplementation((tag) => {
    if (tag !== 'canvas') return {}
    return {
      width: 0,
      height: 0,
      getContext: () => ({ drawImage }),
      toBlob,
    }
  })
  return { drawImage }
}

describe('comprimirImagen', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  it('devuelve el archivo original cuando el navegador no puede decodificarlo', async () => {
    vi.stubGlobal('createImageBitmap', async () => {
      throw new Error('formato no soportado')
    })
    const archivo = archivoFalso('iphone.heic')

    const resultado = await comprimirImagen(archivo)

    expect(resultado).toBe(archivo)
  })

  it('re-codifica a JPEG y deja el nombre con extension .jpg', async () => {
    vi.stubGlobal('createImageBitmap', async () => ({ width: 800, height: 600, close() {} }))
    const toBlob = vi.fn((callback) => callback(new Blob(['x'], { type: 'image/jpeg' })))
    mockCanvas(toBlob)
    const archivo = archivoFalso('captura.png')

    const resultado = await comprimirImagen(archivo)

    expect(resultado.type).toBe('image/jpeg')
    expect(resultado.name).toBe('captura.jpg')
    expect(toBlob).toHaveBeenCalled()
  })

  it('reduce la foto grande al lado maximo', async () => {
    vi.stubGlobal('createImageBitmap', async () => ({ width: 3200, height: 2400, close() {} }))
    const toBlob = vi.fn((callback) => callback(new Blob(['x'], { type: 'image/jpeg' })))
    const { drawImage } = mockCanvas(toBlob)

    await comprimirImagen(archivoFalso('grande.jpg'))

    expect(drawImage).toHaveBeenCalledWith(expect.anything(), 0, 0, 1600, 1200)
  })

  it('no agranda una foto que ya es chica', async () => {
    vi.stubGlobal('createImageBitmap', async () => ({ width: 800, height: 600, close() {} }))
    const toBlob = vi.fn((callback) => callback(new Blob(['x'], { type: 'image/jpeg' })))
    const { drawImage } = mockCanvas(toBlob)

    await comprimirImagen(archivoFalso('chica.jpg'))

    expect(drawImage).toHaveBeenCalledWith(expect.anything(), 0, 0, 800, 600)
  })

  it('devuelve el archivo original si el navegador no tiene canvas', async () => {
    vi.stubGlobal('createImageBitmap', async () => ({ width: 3200, height: 2400, close() {} }))
    vi.spyOn(document, 'createElement').mockImplementation(() => ({
      getContext: () => null,
    }))
    const archivo = archivoFalso('grande.jpg')

    const resultado = await comprimirImagen(archivo)

    expect(resultado).toBe(archivo)
  })

  it('no hace nada con un archivo vacío', async () => {
    const resultado = await comprimirImagen(null)

    expect(resultado).toBe(null)
  })
})
