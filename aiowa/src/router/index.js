// src/router/index.js
import Vue from 'vue';
import Router from 'vue-router';
import DashboardPage from '@/pages/DashboardPage.vue';
// import SettingsPage from '@/pages/SettingsPage.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: DashboardPage
    },
    // {
    //   path: '/settings',
    //   name: 'Settings',
    //   component: SettingsPage
    // },
    {
      path: '*',
      redirect: '/dashboard'
    }
  ]
});
