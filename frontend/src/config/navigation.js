function link(key, label, icon, to, extra = {}) {
  return { key, label, icon, to, ...extra }
}

function section(key, label, items) {
  return { key, label, items }
}

export function createSidebarNavigation({
  isAdmin = false,
  isEncargado = false,
  pendingCount = 0,
} = {}) {
  const primaryItems = [
    link('home', 'Inicio', 'home', { name: 'home' }),
    link('manuales', 'Manuales', 'manual', { name: 'manuales' }),
  ]

  const trailingItems = []
  if (isAdmin) {
    trailingItems.push(link(
      'admin-center',
      'Administración',
      'admin',
      { name: 'admin-center' },
      { activeRoutes: ['admin-center', 'admin-crud', 'admin-configuracion'] },
    ))
  }

  const sections = []
  if (isAdmin || isEncargado) {
    const operationItems = [
      link('dashboard', 'Dashboard Operativo', 'dashboard', { name: 'dashboard' }),
    ]
    if (isAdmin) {
      operationItems.push(
        link('admin-dashboard', 'Dashboard Producción', 'dashboard', { name: 'admin-dashboard' }),
      )
    }
    sections.push(section('operacion', 'Operación', operationItems))
  }

  sections.push(section('combustible', 'Combustible', [
    link('carga-combustible', 'Carga de Combustible', 'fuel', { name: 'combustible' }),
  ]))

  const productionItems = [
    link('carga-produccion', 'Carga de Producción', 'production', { name: 'produccion' }),
    link(
      'pendientes',
      'Pendientes',
      'pending',
      { name: 'pendientes' },
      { badge: Number(pendingCount || 0) },
    ),
  ]
  if (!isEncargado || isAdmin) {
    productionItems.push(
      link('mis-registros', 'Mis Registros', 'records', { name: 'mis-registros' }),
    )
  }
  sections.push(section('produccion', 'Producción', productionItems))

  return { primaryItems, sections, trailingItems }
}

export function flattenNavigation({
  primaryItems = [],
  sections = [],
  trailingItems = [],
}) {
  return [
    ...primaryItems,
    ...sections.flatMap((navigationSection) => navigationSection.items),
    ...trailingItems,
  ]
}
