import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'
import ItemsView from '../views/ItemsView.vue'
import LoginView from '../views/LoginView.vue'
import ProduccionFormView from '../views/ProduccionFormView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false },
  },
  { path: '/', name: 'home', component: HomeView, meta: { requiresAuth: true } },
  { path: '/produccion', name: 'produccion', component: ProduccionFormView, meta: { requiresAuth: true } },
  {
    path: '/combustible',
    name: 'combustible',
    component: () => import('../views/CombustibleFormView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true, requiresEncargado: true },
  },
  {
    path: '/mis-registros',
    name: 'mis-registros',
    component: () => import('../views/OperadorView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/pendientes',
    name: 'pendientes',
    component: () => import('../views/PendientesView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/manuales',
    name: 'manuales',
    component: () => import('../views/ManualesView.vue'),
    meta: { requiresAuth: true },
  },
  { path: '/items', name: 'items', component: ItemsView, meta: { requiresAuth: true } },
  {
    path: '/configuracion',
    name: 'configuracion',
    component: () => import('../views/ConfiguracionView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: { name: 'admin-center' },
      },
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import('../views/admin/AdminDashboardView.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: 'gestion',
        name: 'admin-center',
        component: () => import('../views/admin/AdminCenterView.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: 'crud/:entity',
        name: 'admin-crud',
        component: () => import('../views/admin/AdminCrudView.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: 'configuracion',
        name: 'admin-configuracion',
        component: () => import('../views/admin/ConfiguracionAdminView.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export function authorizeRoute(to, authStore) {
  const authenticated =
    authStore.isAuthenticated || authStore.isAuthenticatedOffline

  if (to.meta.requiresAuth && !authenticated) {
    return { name: 'login' }
  } else if (to.meta.requiresAdmin && authStore.user?.is_admin !== 1) {
    return { name: 'home' }
  } else if (to.meta.requiresEncargado && authStore.user?.encargado !== 1 && authStore.user?.is_admin !== 1) {
    return { name: 'home' }
  } else if (to.name === 'login' && authenticated) {
    return { name: 'home' }
  }

  return true
}

router.beforeEach((to, from, next) => {
  const result = authorizeRoute(to, useAuthStore())
  if (result === true) next()
  else next(result)
})

export default router
