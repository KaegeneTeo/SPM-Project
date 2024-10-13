<template>
    <div class="min-h-full">
        <!-- Sidebar for mobile -->
        <div v-show="mobileMenuOpen" class="fixed inset-0 z-50 flex">
            <div class="relative w-64 bg-gray-800">
                <!-- Close button for sidebar -->
                <div class="absolute top-0 right-0 mt-4 mr-4">
                    <button @click="toggleMobileMenu" class="text-white focus:outline-none">
                        <svg
                            class="h-6 w-6"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke-width="1.5"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                <!-- Mobile navigation links -->
                <nav class="mt-8 px-4 space-y-4">
                    <a
                        @click.prevent="handleLinkClick('Dashboard')"
                        class="block text-white text-lg font-medium"
                        href="#"
                        >Dashboard</a
                    >
                    <a @click.prevent="handleLinkClick('Team')" class="block text-white text-lg font-medium" href="#"
                        >Team</a
                    >
                    <a
                        @click.prevent="handleLinkClick('Schedules')"
                        class="block text-white text-lg font-medium"
                        href="#"
                        >Schedules</a
                    >
                    <a
                        @click.prevent="handleLinkClick('Calendar')"
                        class="block text-white text-lg font-medium"
                        href="#"
                        >Calendar</a
                    >
                    <a
                        @click.prevent="handleLinkClick('Requests')"
                        class="block text-white text-lg font-medium"
                        href="#"
                        >Requests</a
                    >
                </nav>
            </div>
            <div @click="toggleMobileMenu" class="w-full h-full bg-black bg-opacity-50"></div>
        </div>

        <!-- Navigation -->
        <nav class="bg-gray-800">
            <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div class="flex h-16 items-center justify-between">
                    <!-- Logo/Home button -->
                    <div class="flex-shrink-0">
                        <img
                            @click="handleLogoClick"
                            class="h-8 w-8 cursor-pointer"
                            src="https://tailwindui.com/img/logos/mark.svg?color=indigo&shade=500"
                            alt="Your Company" />
                    </div>
                    <!-- Mobile menu button (hamburger) -->
                    <div class="-mr-2 flex md:hidden">
                        <button
                            @click="toggleMobileMenu"
                            type="button"
                            class="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white">
                            <span class="sr-only">Open main menu</span>
                            <svg
                                class="block h-6 w-6"
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke-width="1.5"
                                stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16m-7 6h7" />
                            </svg>
                        </button>
                    </div>
                    <!-- Navigation links -->
                    <div class="hidden md:block">
                        <div class="ml-10 flex items-baseline space-x-4">
                            <a
                                @click.prevent="handleLinkClick('Dashboard')"
                                href="#"
                                class="rounded-md text-gray-300 hover:bg-gray-700 px-3 py-2 text-sm font-medium text-white"
                                >Dashboard</a
                            >
                            <a
                                @click.prevent="handleLinkClick('Team')"
                                href="#"
                                class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
                                >Team</a
                            >
                            <a
                                @click.prevent="handleLinkClick('Schedules')"
                                href="#"
                                class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
                                >Schedules</a
                            >
                            <a
                                @click.prevent="handleLinkClick('Calendar')"
                                href="#"
                                class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
                                >Calendar</a
                            >
                            <a
                                @click.prevent="handleLinkClick('Requests')"
                                href="#"
                                class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
                                >Requests</a
                            >
                        </div>
                    </div>
                    <!-- Notifications button -->
                    <div class="hidden md:block">
                        <div class="ml-4 flex items-center md:ml-6">
                            <button
                                @click="handleNotificationsClick"
                                type="button"
                                class="relative rounded-full bg-gray-800 p-1 text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800">
                                <span class="absolute -inset-1.5"></span>
                                <span class="sr-only">View notifications</span>
                                <svg
                                    class="h-6 w-6"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke-width="1.5"
                                    stroke="currentColor"
                                    aria-hidden="true">
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
                                </svg>
                            </button>
                            <!-- Profile dropdown -->
                            <div class="relative ml-3">
                                <div>
                                    <button
                                        @click="toggleDropdown"
                                        type="button"
                                        class="relative flex max-w-xs items-center rounded-full bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                                        id="user-menu-button"
                                        aria-expanded="false"
                                        aria-haspopup="true">
                                        <span class="absolute -inset-1.5"></span>
                                        <span class="sr-only">Open user menu</span>
                                        <img
                                            class="h-8 w-8 rounded-full"
                                            src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                                            alt="" />
                                    </button>
                                </div>
                                <!-- Dropdown menu -->
                                <div
                                    v-show="showDropdown"
                                    class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                                    role="menu"
                                    aria-orientation="vertical"
                                    tabindex="-1">
                                    <a
                                        @click.prevent="handleLinkClick('Profile')"
                                        href="#"
                                        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        role="menuitem"
                                        tabindex="-1"
                                        >Your Profile</a
                                    >
                                    <a
                                        @click.prevent="handleLinkClick('Settings')"
                                        href="#"
                                        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        role="menuitem"
                                        tabindex="-1"
                                        >Settings</a
                                    >
                                    <a
                                        @click.prevent="handleSignOut('Login')"
                                        href="#"
                                        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        role="menuitem"
                                        tabindex="-1"
                                        >Sign out</a
                                    >
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </nav>

        <main>
            <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <slot></slot>
                <!-- Content will be injected here -->
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios"; // Import axios

// Routing
const router = useRouter();

// Props
const props = defineProps({
    title: {
        type: String,
        default: "Dashboard",
    },
});

// Reactive states
const showDropdown = ref(false);
const mobileMenuOpen = ref(false);

// Methods
function toggleDropdown() {
    showDropdown.value = !showDropdown.value;
}

function toggleMobileMenu() {
    mobileMenuOpen.value = !mobileMenuOpen.value;
}

function handleLinkClick(linkName) {
    router.push(`/${linkName.toLowerCase()}`);
}

// Sign out method
async function handleSignOut() {
    try {
        // Call your endpoint to clear the session on the server
        await axios.post("http://127.0.0.1:5000/logout", {
            access_token: localStorage.getItem("access_token"),
        });

        // Clear the session data from localStorage
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user_email");
        localStorage.removeItem("staff_id");
        localStorage.removeItem("role");
        localStorage.removeItem("dept");
        localStorage.removeItem("reporting_manager");

        // Log the sign-out action and navigate to the login page
        console.log("Signed out!");
        router.push("/login");
    } catch (error) {
        console.error("Error during sign out:", error);
    }
}
</script>
