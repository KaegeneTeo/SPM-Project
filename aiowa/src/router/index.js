import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'
import Schedule from '../views/Schedule.vue'
import Request from '../views/Request.vue'
import NewRequest from '../views/NewRequest.vue'

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
      path: '/schedules',
      name: 'schedules',
      component: Schedule
    },
    {
      path: '/requests',
      name: 'requests',
      component: Request
    },
    {
      path: '/newrequest',
      name: 'newrequest',
      component: NewRequest
    }
  ]
})

export default router
