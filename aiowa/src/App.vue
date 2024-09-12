<template>
  <div class="min-h-full">
    <!-- Mobile Sidebar -->
    <Sidebar
      :mobileMenuOpen="mobileMenuOpen"
      :toggleMobileMenu="toggleMobileMenu"
      :handleLinkClick="handleLinkClick"
    />

    <!-- Main Navigation -->
    <Navigation
      :showDropdown="showDropdown"
      :mobileMenuOpen="mobileMenuOpen"
      :toggleDropdown="toggleDropdown"
      :toggleMobileMenu="toggleMobileMenu"
      :handleLinkClick="handleLinkClick"
      :handleNotificationsClick="handleNotificationsClick"
      :handleLogoClick="handleLogoClick"
    />

    <!-- Page Header -->
    <header class="bg-white shadow">
      <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Dashboard</h1>
      </div>
    </header>

    <!-- Main Content -->
    <main>
      <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <!-- Your content goes here -->
      </div>
    </main>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue';
import Navigation from './components/Navigation.vue';

export default {
  components: {
    Sidebar,
    Navigation
  },
  data() {
    return {
      showDropdown: false,
      mobileMenuOpen: false
    };
  },
  methods: {
    handleLinkClick(linkName) {
      alert(`${linkName} link clicked!`);
    },
    handleNotificationsClick() {
      alert('Notifications clicked!');
    },
    handleLogoClick() {
      alert('Home clicked!');
    },
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen;
    },
    profilePage() {
      alert('Profile page clicked!');
    },
    settingPage() {
      alert('Settings clicked');
    },
    loginPage() {
      alert('Login page clicked!');
    }
  }
}
</script>

<style>
@import './assets/tailwind.css';
</style>
