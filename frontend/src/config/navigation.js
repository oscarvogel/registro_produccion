function link(key, label, icon, to, extra = {}) {
  return { type: 'link', key, label, icon, to, ...extra }
}

function section(key, label, icon, items) {
  return { type: 'section', key, label, icon, items }
}

export function createNavigationAreas({ isAdmin = false, isEncargado = false, pendingCount = 0 } = {}) {
  const productionItems = [
    link('carga-produccion', 'Cargar producción', 'production', { name: 'produccion' }),
    link('pendientes', 'Pendientes', 'pending', { name: 'pendientes' }, { badge: Number(pendingCount || 0) }),
  ]

  if (!isEncargado || isAdmin) {
    productionItems.push(link('mis-registros', 'Mis registros', 'records', { name: 'mis-registros' }))
  }

  const areas = [
    link('home', 'Inicio', 'home', { name: 'home' }),
    section('produccion', 'Producción', 'production', productionItems),
    link('combustible', 'Combustible', 'fuel', { name: 'combustible' }),
  ]

  if (isAdmin || isEncargado) {
    const dashboardItems = [
      link('dashboard-operativo', 'Dashboard operativo', 'dashboard', { name: 'dashboard' }),
    ]
    if (isAdmin) {
      dashboardItems.push(link('resumen-ejecutivo', 'Resumen ejecutivo', 'dashboard', { name: 'admin-dashboard' }))
    }
    areas.push(section('dashboard', 'Dashboard', 'dashboard', dashboardItems))
  }

  if (isAdmin) {
    areas.push(link(
      'admin-center',
      'Administración',
      'admin',
      { name: 'admin-center' },
      { activeRoutes: ['admin-center', 'admin-crud', 'admin-configuracion'] },
    ))
  }

  return areas
}

export function flattenNavigationItems(areas) {
  return areas.flatMap((area) => area.type === 'section' ? area.items : [area])
}
