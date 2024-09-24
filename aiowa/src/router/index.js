import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios';
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'
import Schedule from '../views/Schedule.vue'
import Request from '../views/Request.vue'
import NewRequest from '../views/NewRequest.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { requiresAuth: true } // Restricted route
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/schedules',
      name: 'schedules',
      component: Schedule,
      meta: { requiresAuth: true }
    },
    {
      path: '/requests',
      name: 'requests',
      component: Request,
      meta: { requiresAuth: true }
    },
    {
      path: '/newrequest',
      name: 'newrequest',
      component: NewRequest,
      meta: { requiresAuth: true }
    },
    {
      path: '/team',
      name: 'team',
      // component: Team,
      meta: { requiresAuth: true }
    },
    {
      path: '/calendar',
      name: 'calendar',
      // component: Calendar,
      meta: { requiresAuth: true }
    }
  ]
})




export default router
