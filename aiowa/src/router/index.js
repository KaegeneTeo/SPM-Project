import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios';
import Login from '../views/Login.vue'
import Schedule from '../views/Schedule.vue'
import MySchedule from '../views/MySchedule.vue'
import Request from '../views/Request.vue'
import NewRequest from '../views/NewRequest.vue'
import ViewRequestStaff from '../views/ViewRequestStaff.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
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
      path: '/myschedule',
      name: 'schedule',
      component: MySchedule,
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
      path: '/viewrequeststaff',
      name: 'viewrequeststaff',
      component : ViewRequestStaff,
      meta: {requiresAuth: true}
    },
    {
      path: '/team',
      name: 'team',
      // component: Team,
      meta: { requiresAuth: true }
    }
  ]
})




export default router
