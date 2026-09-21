function link(key, label, icon, to, extra = {}) {
  return { key, label, icon, to, ...extra }
}

function section(key, label, items, icon = key) {
  return { key, label, items, icon }
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
      link('dashboard', 'Operación', 'dashboard', { name: 'dashboard' }, {
        activeRoutes: ['dashboard-registros'],
      }),
    ]
    if (isAdmin) {
      operationItems.push(
        link('admin-dashboard', 'Análisis de Producción', 'analysis', { name: 'admin-dashboard' }),
      )
    }
    sections.push(section('operacion', 'Seguimiento', operationItems, 'tracking'))
  }

  sections.push(section('combustible', 'Combustible', [
    link('carga-combustible', 'Carga de Combustible', 'fuel-add', { name: 'combustible' }),
  ], 'fuel'))

  const productionItems = [
    link('carga-produccion', 'Carga de Producción', 'production-add', { name: 'produccion' }),
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
  sections.push(section('produccion', 'Producción', productionItems, 'production'))

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

const mobileNavigationKeys = {
  operator: ['home', 'carga-produccion', 'carga-combustible', 'pendientes'],
  encargado: ['home', 'dashboard', 'carga-produccion', 'pendientes'],
  admin: ['home', 'dashboard', 'admin-dashboard', 'admin-center'],
}

const mobileLabels = {
  'carga-produccion': 'Producción',
  'carga-combustible': 'Combustible',
  'admin-dashboard': 'Análisis',
  'admin-center': 'Admin',
}

export function createMobileNavigation({ isAdmin = false, isEncargado = false, pendingCount = 0 } = {}) {
  const role = isAdmin ? 'admin' : isEncargado ? 'encargado' : 'operator'
  const navigation = createSidebarNavigation({ isAdmin, isEncargado, pendingCount })
  const itemsByKey = new Map(flattenNavigation(navigation).map((item) => [item.key, item]))

  return mobileNavigationKeys[role]
    .map((key) => itemsByKey.get(key))
    .filter(Boolean)
    .map((item) => ({
      ...item,
      mobileLabel: mobileLabels[item.key] || item.label,
      accessibleLabel: item.label,
    }))
}

export function createMobileMoreGroups({ isAdmin = false, isEncargado = false, pendingCount = 0 } = {}) {
  const navigation = createSidebarNavigation({ isAdmin, isEncargado, pendingCount })
  const directKeys = new Set(createMobileNavigation({ isAdmin, isEncargado, pendingCount }).map((item) => item.key))
  const groups = []

  function addGroup(key, label, items) {
    const availableItems = items
      .filter((item) => !directKeys.has(item.key))
      .map((item) => ({ ...item, accessibleLabel: item.label }))

    if (availableItems.length > 0) groups.push({ key, label, items: availableItems })
  }

  addGroup('general', 'General', navigation.primaryItems)
  navigation.sections.forEach((section) => addGroup(section.key, section.label, section.items))
  addGroup('administracion', 'Administración', navigation.trailingItems)

  return groups
}

export function isNavigationItemActive(item, route) {
  if (!item || !route) return false
  if (item.activeRoutes?.includes(route.name)) return true
  if (item.to?.name === 'admin-crud') {
    return route.name === 'admin-crud' && route.params?.entity === item.to.params?.entity
  }
  return route.name === item.to?.name
}

export function shouldShowMobileBottomNavigation(routeName) {
  return !['produccion', 'combustible'].includes(routeName)
}
