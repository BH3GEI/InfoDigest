import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/subscriptions',
      name: 'subscriptions',
      component: () => import('../views/SubscriptionsView.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue')
    },
    {
      path: '/reader',
      name: 'reader',
      component: () => import('../views/ReaderView.vue')
    },
    {
      path: '/reader/:filename',
      name: 'reader-detail',
      component: () => import('../views/ReaderDetailView.vue')
    }
  ]
})

export default router