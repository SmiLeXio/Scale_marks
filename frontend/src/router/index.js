import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/auth',
      component: () => import('../views/AuthView.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      component: () => import('../views/AppShell.vue'),
      children: [
        { path: '', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
        { path: 'pets', name: 'pets', component: () => import('../views/PetsView.vue') },
        { path: 'pets/new', name: 'pet-new', component: () => import('../views/PetFormView.vue') },
        { path: 'pets/:id/edit', name: 'pet-edit', component: () => import('../views/PetFormView.vue') },
        { path: 'growth', name: 'growth', component: () => import('../views/GrowthView.vue') },
        { path: 'feeding', name: 'feeding', component: () => import('../views/FeedingView.vue') },
        { path: 'calendar', name: 'calendar', component: () => import('../views/CalendarView.vue') }
      ]
    }
  ]
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.initialized) {
    await auth.init()
  }
  if (!to.meta.public && !auth.isAuthenticated) {
    return '/auth'
  }
  if (to.meta.public && auth.isAuthenticated) {
    return '/'
  }
  return true
})

export default router
