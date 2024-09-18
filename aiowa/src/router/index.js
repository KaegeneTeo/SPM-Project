import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'
import Schedule from '../views/Schedule.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
        path: '/dashboard',
        name: 'dashboard',
        component: Dashboard
    },
    {
        path: '/login',
        name: 'login',
        component: Login
    },
    {
      path: '/schedule',
      name: 'schedule',
      component: Schedule
  }
  ]
})

export default router
