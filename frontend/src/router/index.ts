import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/views/Layout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/Dashboard.vue')
        },
        {
          path: 'companies',
          name: 'companies',
          component: () => import('@/views/Companies.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: 'projects',
          name: 'projects',
          component: () => import('@/views/Projects.vue')
        },
        {
          path: 'projects/:id',
          name: 'project-detail',
          component: () => import('@/views/ProjectDetail.vue')
        },
        {
          path: 'test-cases',
          name: 'test-cases',
          component: () => import('@/views/TestCases.vue')
        },
        {
          path: 'test-cases/:id',
          name: 'test-case-detail',
          component: () => import('@/views/TestCaseDetail.vue')
        },
        {
          path: 'test-executions',
          name: 'test-executions',
          component: () => import('@/views/TestExecutions.vue')
        },
        {
          path: 'test-reports',
          name: 'test-reports',
          component: () => import('@/views/TestReports.vue')
        },
        {
          path: 'test-reports/:id',
          name: 'test-report-detail',
          component: () => import('@/views/TestReportDetail.vue')
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('@/views/Users.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/Profile.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFound.vue')
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    next('/')
  } else {
    next()
  }
})

export default router