<!-- src/components/LayoutComponent.vue -->
<template>
  <div class="min-h-full">
    <!-- Navigation and sidebar here -->
    <nav class="bg-gray-800">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 items-center justify-between">
          <!-- Logo/Home button -->
          <div class="flex-shrink-0">
            <img @click="handleLogoClick" class="h-8 w-8 cursor-pointer" src="https://tailwindui.com/img/logos/mark.svg?color=indigo&shade=500" alt="Your Company">
          </div>
          
          <!-- Navigation links -->
          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <a href="#" @click.prevent="handleLinkClick('Dashboard')" class="rounded-md bg-gray-900 px-3 py-2 text-sm font-medium text-white">Dashboard</a>
              <a href="#" @click.prevent="handleLinkClick('Team')" class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white">Team</a>
              <a href="#" @click.prevent="handleLinkClick('Projects')" class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white">Projects</a>
              <a href="#" @click.prevent="handleLinkClick('Calendar')" class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white">Calendar</a>
              <a href="#" @click.prevent="handleLinkClick('Reports')" class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white">Reports</a>
            </div>
          </div>

          <!-- Notifications and profile buttons -->
          <div class="hidden md:block">
            <div class="ml-4 flex items-center md:ml-6">
              <button @click="handleNotificationsClick" type="button" class="relative rounded-full bg-gray-800 p-1 text-gray-400 hover:text-white">
                <span class="sr-only">View notifications</span>
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
                </svg>
              </button>

              <!-- Profile dropdown -->
              <div class="relative ml-3">
                <button @click="toggleDropdown" type="button" class="relative flex max-w-xs items-center rounded-full bg-gray-800 text-sm focus:outline-none">
                  <span class="sr-only">Open user menu</span>
                  <img class="h-8 w-8 rounded-full" src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" alt="">
                </button>
                
                <div v-show="showDropdown" class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg">
                  <a href="#" @click="profilePage" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Your Profile</a>
                  <a href="#" @click="settingPage" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Settings</a>
                  <a href="#" @click="loginPage" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Sign out</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Mobile sidebar -->
    <div class="md:hidden" v-show="sidebarOpen">
      <div class="fixed inset-0 bg-gray-600 bg-opacity-75" @click="toggleSidebar"></div>
      <div class="fixed inset-0 flex">
        <div class="relative flex w-64 flex-col overflow-y-auto bg-gray-800">
          <div class="flex h-16 items-center justify-between px-4">
            <button @click="toggleSidebar" class="text-gray-400 hover:text-white">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <nav class="mt-2 px-2">
            <a href="#" @click.prevent="handleLinkClick('Dashboard')" class="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">Dashboard</a>
            <a href="#" @click.prevent="handleLinkClick('Team')" class="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">Team</a>
            <a href="#" @click.prevent="handleLinkClick('Projects')" class="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">Projects</a>
            <a href="#" @click.prevent="handleLinkClick('Calendar')" class="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">Calendar</a>
            <a href="#" @click.prevent="handleLinkClick('Reports')" class="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">Reports</a>
          </nav>
        </div>
      </div>
    </div>

    <!-- Page-specific content slot -->
    <main>
      <slot></slot>
    </main>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showDropdown: false,
      sidebarOpen: false
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
    profilePage() {
      alert('Profile page clicked!');
    },
    settingPage() {
      alert('Settings clicked!');
    },
    loginPage() {
      alert('Login page clicked!');
    },
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    }
  }
};
</script>

<style scoped>
/* Add any layout-specific styles here */
</style>
