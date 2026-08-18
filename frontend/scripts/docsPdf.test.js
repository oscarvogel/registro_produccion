import { describe, expect, it } from 'vitest'
import { imageToDataUri } from './docsPdf.mjs'

describe('generación de manuales PDF', () => {
  it('falla con un mensaje claro cuando falta una imagen obligatoria', async () => {
    await expect(imageToDataUri('/manuales/capturas/no-existe.png'))
      .rejects.toThrow('Falta la captura o imagen referenciada')
  })
})
