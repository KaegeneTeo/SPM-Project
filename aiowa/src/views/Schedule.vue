<script>
import MainLayout from "../components/MainLayout.vue"
import VueCal from "../components/VueCal.vue";
import 'vue-cal/dist/vuecal.css'; // vue-cal's styles

export default {
  components: {
    VueCal // Registering the component
  }
};
</script>

<template>
  <div class="min-h-full">
    <MainLayout>
        <header class="bg-white">
            <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <h1 class="text-3xl font-bold tracking-tight text-gray-900">Schedules</h1>
            </div>
        </header>

        <!-- Your main content goes here -->
        <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 grid grid-cols-12 gap-4">
        
            <!-- Left column: Dropdown -->
            <div class="col-span-12 lg:col-span-3">
                <label for="schedule-selector" class="block text-sm font-medium text-gray-700">Select Schedule:</label>
                <select id="schedule-selector" class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                    <option>Schedule 1</option>
                    <option>Schedule 2</option>
                    <option>Schedule 3</option>
                </select>
            </div>

            <!-- Middle column: VueCal Calendar -->
            <div class="col-span-12 lg:col-span-6">
                <VueCal
                    :events="calendarEvents"
                    :hide-weekends="true"
                    :events-count-on-year-view="5"
                    @event-click="handleEventClick"
                />
            </div>


            <!-- Right column: Legend -->
            <div class="col-span-12 lg:col-span-3">
                <h2 class="text-lg font-semibold text-gray-900">Legend</h2>
                <ul class="mt-2 space-y-1">
                    <li class="flex items-center">
                    <span class="inline-block h-4 w-4 bg-orange-500 rounded-full mr-2"></span> AM
                    </li>
                    <li class="flex items-center">
                    <span class="inline-block h-4 w-4 bg-purple-500 rounded-full mr-2"></span> PM
                    </li>                    
                </ul>
            </div>
        </main>
    </MainLayout>
  </div>
</template>