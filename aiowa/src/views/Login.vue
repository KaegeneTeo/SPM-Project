<!--
  This example requires some changes to your config:
  
  ```
  // tailwind.config.js
  module.exports = {
    // ...
    plugins: [
      // ...
      require('@tailwindcss/forms'),
    ],
  }
  ```
-->
<template>
    <!--
      This example requires updating your template:
  
      ```
      <html class="h-full bg-white">
      <body class="h-full">
      ```
    -->
    <div class="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
        <div class="sm:mx-auto sm:w-full sm:max-w-sm">
            <img
                class="mx-auto h-40 w-auto sm:h-60 lg:h-72"
                src="../assets/aiowa-photoaidcom-cropped.png"
                alt="Your Company" />
            <h2 class="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                Sign in to your account
            </h2>
        </div>

        <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
            <form class="space-y-6" @submit.prevent="handleLogin" method="POST">
                <div>
                    <label for="email" class="block text-sm font-medium leading-6 text-gray-900">Email address</label>
                    <div class="mt-2">
                        <input
                            v-model="email"
                            id="email"
                            name="email"
                            type="email"
                            autocomplete="email"
                            required
                            class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 p-2" />
                    </div>
                </div>

                <div>
                    <div class="flex items-center justify-between">
                        <label for="password" class="block text-sm font-medium leading-6 text-gray-900">Password</label>
                    </div>
                    <div class="mt-2">
                        <input
                            v-model="password"
                            id="password"
                            name="password"
                            type="password"
                            autocomplete="current-password"
                            required
                            class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 p-2" />
                    </div>
                </div>

                <div v-if="errorMessage" class="text-red-500 text-sm">
                    {{ errorMessage }}
                </div>

                <div>
                    <button
                        type="submit"
                        class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                        Sign in
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router"; // Import the router
const   VITE_AWS_URL = import.meta.env.VITE_AWS_URL

export default {
    setup() {
        const email = ref("");
        const password = ref("");
        const errorMessage = ref("");
        const router = useRouter(); // Access router

        const handleLogin = async () => {
            try {
                
                const response = await axios.post(`${VITE_AWS_URL}/login`, {
                    email: email.value,
                    password: password.value,
                });


                if (response.data) {
                    localStorage.setItem("access_token", response.data.access_token);
                    localStorage.setItem("refresh_token", response.data.refresh_token);
                    localStorage.setItem("user_email", response.data.email);
                    localStorage.setItem("staff_id", response.data.staff_id)
                    localStorage.setItem("role", response.data.role)
                    localStorage.setItem("dept", response.data.dept)
                    localStorage.setItem("reporting_manager",response.data.reporting_manager);
                    router.push("/schedules");
                }
            } catch (error) {
                console.error("Login failed:", error);
                errorMessage.value = "Invalid email or password. Please try again.";
            }
        };

        const handleLinkClick = (linkName) => {
            router.push(`/${linkName.toLowerCase()}`);
        };

        return { email, password, handleLogin, handleLinkClick, errorMessage };
    },
};
</script>

<style scoped>
/* Your styles here */
</style>
