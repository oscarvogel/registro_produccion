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
        redirect: { name: 'dashboard' },
      },
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import('../views/admin/AdminDashboardView.vue'),
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

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.meta.requiresAdmin && authStore.user?.is_admin !== 1) {
    next({ name: 'home' })
  } else if (to.meta.requiresEncargado && authStore.user?.encargado !== 1 && authStore.user?.is_admin !== 1) {
    next({ name: 'home' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
