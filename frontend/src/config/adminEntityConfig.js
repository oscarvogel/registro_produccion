export const ADMIN_ENTITY_CONFIG = {
  personal: { endpoint: '/api/admin/personal', idKey: 'idPersonal', label: 'Personal' },
  moviles: { endpoint: '/api/admin/moviles', idKey: 'idMovil', label: 'Moviles' },
  'unidades-negocio': { endpoint: '/api/admin/unidades-negocio', idKey: 'idUnidadNegocio', label: 'Unidades de Negocio' },
  'tipos-proceso': { endpoint: '/api/admin/tipos-proceso', idKey: 'id', label: 'Tipos de Proceso' },
  'tipos-movil': { endpoint: '/api/admin/tipos-movil', idKey: 'id', label: 'Tipos de Movil' },
  'lugares-carga': { endpoint: '/api/admin/lugares-carga', idKey: 'idLugarCarga', label: 'Lugares de Carga' },
  // Catalogo legacy de clientes: `predios.empresa` es FK contra `cliente.cuit`.
  // Son mas de 2000 filas, asi que la referencia se trae con un limite mayor
  // al que usa el resto de las entidades.
  clientes: {
    endpoint: '/api/admin/clientes',
    idKey: 'cuit',
    label: 'Clientes',
    referenceLimit: 3000,
  },
  predios: { endpoint: '/api/admin/predios', idKey: 'idPredio', label: 'Predios' },
  rodales: { endpoint: '/api/admin/rodales', idKey: 'idRodal', label: 'Rodales' },
  actas: { endpoint: '/api/admin/actas', idKey: 'id', label: 'Actas' },
  asignaciones: { endpoint: '/api/admin/asignaciones', idKey: 'idAsignacion', label: 'Asignaciones Operativas' },
}
