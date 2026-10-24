// Compresion de la foto de evidencia antes de subirla (issue #200).
//
// En la planta la senal es mala: una foto de 4 MB tarda mucho y se corta a
// mitad de camino. El navegador redimensiona a un lado mayor de 1600 px y
// re-codifica a JPEG calidad 0.8, que para leer un horometro alcanza de
// sobra y pesa una fracción.
//
// Si el navegador no puede decodificar la imagen (HEIC de iPhone, por
// ejemplo), se devuelve el archivo original: el backend acepta image/heic.

export const MAX_LADO_IMAGEN = 1600
export const CALIDAD_JPEG = 0.8

function nombreComoJpeg(nombre) {
  const base = String(nombre || 'evidencia').replace(/\.[^.]+$/, '')
  return `${base || 'evidencia'}.jpg`
}

// Decodifica el archivo a un bitmap. Devuelve null si el navegador no lo
// entiende.
async function decodificar(file) {
  if (typeof createImageBitmap === 'function') {
    try {
      return await createImageBitmap(file)
    } catch {
      return null
    }
  }
  if (typeof Image === 'undefined' || typeof URL?.createObjectURL !== 'function') {
    return null
  }
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file)
    const imagen = new Image()
    imagen.onload = () => {
      URL.revokeObjectURL(url)
      resolve(imagen)
    }
    imagen.onerror = () => {
      URL.revokeObjectURL(url)
      resolve(null)
    }
    imagen.src = url
  })
}

function dibujarEnCanvas(bitmap, ancho, alto) {
  if (typeof document === 'undefined') return null
  const canvas = document.createElement('canvas')
  canvas.width = ancho
  canvas.height = alto
  const ctx = canvas.getContext?.('2d')
  // En jsdom (tests) no hay canvas: se devuelve el archivo original.
  if (!ctx) return null
  ctx.drawImage(bitmap, 0, 0, ancho, alto)
  return canvas
}

export async function comprimirImagen(file, opciones = {}) {
  const maxLado = Number(opciones.maxLado || MAX_LADO_IMAGEN)
  const calidad = Number(opciones.calidad || CALIDAD_JPEG)

  if (!file) return file

  const bitmap = await decodificar(file)
  if (!bitmap) return file

  const anchoOriginal = bitmap.width || bitmap.naturalWidth || 0
  const altoOriginal = bitmap.height || bitmap.naturalHeight || 0
  if (!anchoOriginal || !altoOriginal) {
    if (typeof bitmap.close === 'function') bitmap.close()
    return file
  }

  const escala = Math.min(1, maxLado / Math.max(anchoOriginal, altoOriginal))
  const ancho = Math.max(1, Math.round(anchoOriginal * escala))
  const alto = Math.max(1, Math.round(altoOriginal * escala))

  const canvas = dibujarEnCanvas(bitmap, ancho, alto)
  if (typeof bitmap.close === 'function') bitmap.close()
  if (!canvas) return file

  const blob = await new Promise((resolve) => {
    if (typeof canvas.toBlob !== 'function') {
      resolve(null)
      return
    }
    canvas.toBlob(resolve, 'image/jpeg', calidad)
  })
  if (!blob) return file

  const nombre = nombreComoJpeg(file.name)
  if (typeof File === 'function') {
    return new File([blob], nombre, { type: 'image/jpeg', lastModified: Date.now() })
  }
  return Object.assign(blob, { name: nombre })
}
