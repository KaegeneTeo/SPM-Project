<template>
      <MainLayout title="Dashboard" v-if="!isLoginPage">
      <!-- Render the router-view inside the MainLayout when not on the login page -->
      <router-view />
    </MainLayout>

    <!-- Render the router-view directly when on the login page -->
    <router-view v-else />
</template>

<script>
import { computed } from 'vue';
import { useRoute } from 'vue-router'; // Import useRoute to access the current route
import MainLayout from './components/MainLayout.vue';

export default {
  components: {
    MainLayout,
  },
  setup() {
    const route = useRoute(); // Access the current route

    // Compute whether the current route is the login page
    const isLoginPage = computed(() => route.name === 'login');

    return { isLoginPage };
  },
};
</script>

<style scoped>
/* Your styles here */
</style>

