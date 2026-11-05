import { describe, expect, it } from 'vitest'

import { ADMIN_ENTITY_CONFIG } from './adminEntityConfig'

describe('adminEntityConfig', () => {
  it('expone el catalogo legacy de clientes con el CUIT como clave', () => {
    expect(ADMIN_ENTITY_CONFIG.clientes).toMatchObject({
      endpoint: '/api/admin/clientes',
      idKey: 'cuit',
      label: 'Clientes',
      referenceLimit: 3000,
    })
  })
})
