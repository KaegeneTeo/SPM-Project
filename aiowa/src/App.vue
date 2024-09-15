<template>
  <MainLayout title="Dashboard">
    <!-- Your main content goes here -->
    <router-view></router-view> <!-- This will render the component corresponding to the current route -->
  </MainLayout>
</template>

<script setup>
import MainLayout from './components/MainLayout.vue'
</script>
