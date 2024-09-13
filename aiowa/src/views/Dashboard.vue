<script>
import MainLayout from "../components/MainLayout.vue"
</script>

<template>
  <div class="min-h-full">
    <MainLayout>
      <header class="bg-white">
        <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Dashboard</h1>
        </div>
      </header>

      <!-- Your main content goes here -->
      <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <router-view></router-view> <!-- This will render the component corresponding to the current route -->
      </main>
    </MainLayout>
  </div>
</template>
