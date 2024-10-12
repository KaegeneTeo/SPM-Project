<script>
import MainLayout from "../components/MainLayout.vue"
import VueCal from 'vue-cal'
import 'vue-cal/dist/vuecal.css'
import axios from "axios";

export default {
    components: {
        VueCal // Registering the component
    },
    data() {
        return {
            selectedEvent: {},
            showDialog: false,
            role: null,
            selectedDept: "",   // Stores the currently selected department
            selectedTeam: "",   // Stores the currently selected team
            dept: ["CEO", "Consultancy", "Engineering", "Finance", "HR", "IT", "Sales", "Solutioning"],
            filteredTeams: [],  // Initialize filteredTeams to hold teams for the selected department
            events: [
                {
                    start: '2024-09-19 09:00',
                    end: '2024-09-19 13:00',
                    title: '1',
                    class: 'AM',
                    count: 1,
                    nameList: [
                        {
                            staff_id: 0,
                            name: "John"
                        }
                    ]
                },
                {
                    start: '2024-09-19 14:00',
                    end: '2024-09-19 18:00',
                    title: '3',
                    class: 'PM',
                    count: 3,
                    nameList: [
                        {
                            staff_id: 3,
                            name: "Bob"
                        },
                        {
                            staff_id: 4,
                            name: "Alice"
                        },
                        {
                            staff_id: 1,
                            name: "Jane"
                        }
                    ]
                }
            ]
        }
    },
    mounted() {
        // Retrieve the role from localStorage when the component is mounted
        this.role = localStorage.getItem('role');
        const teamData = localStorage.getItem('team');
        this.team = teamData ? JSON.parse(teamData).sort() : [];
    },
    watch: {
        selectedDept(newDept) {
            this.fetchTeams(newDept); // Fetch teams whenever the department changes
            this.selectedTeam = "";    // Reset the selected team
        }
    },
    methods: {
        async fetchTeams(department) {
            if (!department) {
                this.filteredTeams = []; // Clear teams if no department is selected
                return;
            }
            try {
                const response = await axios.get(`http://127.0.0.1:5000/teams_by_dept`, {
                    params: { department } // Pass department as a query parameter
                });

                this.filteredTeams = response.data; // Update filteredTeams with the fetched data
            } catch (error) {
                console.error("Error fetching teams:", error);
            }
        },
        search() {
            let params = {};
            if (this.role === '1') {
                params = { dept: this.selectedDept, team: this.selectedTeam.replace('Team ', '') };
                console.log(params);
            } else if (this.role === '3') {
                params = { dept: localStorage.getItem('dept'),team: this.selectedTeam.replace('Team ', '') };
                console.log(params);
            }

            axios.get('http://127.0.0.1:5000/schedules', { params })
                .then(response => {
                    this.events = response.data.schedules;
                })
                .catch(error => {
                    console.error("Error fetching schedules: ", error);
                });
        },
        AMCount(events) {
            return events.reduce((acc, event) => event.class === "AM" ? acc + event.count : acc, 0);
        },
        PMCount(events) {
            return events.reduce((acc, event) => event.class === "PM" ? acc + event.count : acc, 0);
        },
        onEventClick(event, e) {
            this.selectedEvent = event;
            this.showDialog = true;
            e.stopPropagation(); // Prevent default behavior
        }
    }
};
</script>

<template>
    <div class="min-h-full">
        <MainLayout>
            <header class="bg-white">
                <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Schedules</h1>                                                     <!--FOR FILTERS, ONLY TEST WITH DEPT:SALES,CEO,HR-->
                </div>
            </header>

            <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 grid grid-cols-12 gap-4">
                <!-- Left column: Conditional Dropdowns based on role -->

                <!-- Role 1: Show both Department and Team filters -->
                <div v-if="role === '1'" class="col-span-12 lg:col-span-3">
                    <div>
                        <label for="schedule-selector-department" class="block text-sm font-medium text-gray-700">Select Department:</label>
                        <select v-model="selectedDept" id="schedule-selector-department" class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                            <option value="">Select a department</option>
                            <option v-for="item in dept" :key="item" :value="item">{{ item }}</option>
                        </select>
                    </div>
                    <div class="mt-4">
                        <label for="schedule-selector-team" class="block text-sm font-medium text-gray-700">Select Team:</label>
                        <select v-model="selectedTeam" id="schedule-selector-team" class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                            <option value="">Select a team</option>
                            <option v-for="item in filteredTeams" :key="item">Team {{ item }}</option>
                        </select>
                    </div>
                    <!-- Search Button -->
                    <div class="mt-6">
                        <button id="search-button" @click="search" class="bg-indigo-500 text-white px-4 py-2 rounded-md shadow-sm hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50">
                            Search
                        </button>
                    </div>
                </div>

                <!-- Role 2: No filters, no search button (nothing rendered here) -->
                <div v-if="role === '2'" class="col-span-12 lg:col-span-3"></div>

                <!-- Role 3: Show only Team filter and Search button -->
                <div v-if="role === '3'" class="col-span-12 lg:col-span-3">
                    <div>
                        <label for="schedule-selector-team" class="block text-sm font-medium text-gray-700">Select Team:</label>
                        <select v-model="selectedTeam" id="schedule-selector-team" class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                            <option value="">Select a team</option>
                            <option v-for="item in team" :key="item">Team {{ item }}</option>
                        </select>
                    </div>
                    <!-- Search Button -->
                    <div class="mt-6">
                        <button id="search-button" @click="search" class="bg-indigo-500 text-white px-4 py-2 rounded-md shadow-sm hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50">
                            Search
                        </button>
                    </div>
                </div>

                <!-- Middle column: VueCal Calendar for HR and Manager -->
                <div v-if="role != 2" class="col-span-12 lg:col-span-6">
                    <VueCal class="vuecal--blue-theme" style="height: 500px;" :events="events" :hide-weekends="true" events-count-on-year-view :on-event-click="onEventClick" :time-from="9 * 60" :time-to="18 * 60">
                        <template #cell-content="{ cell, view, goNarrower, events }">
                            <span class="vuecalcell-date" :class="view.id" @click="goNarrower">
                                <span class="clickable">{{ cell.content }}</span>
                            </span>
                            <span class="vuecalcell-events-count" v-if="['years', 'year', 'month'].includes(view.id) && events.length">
                                <span class="am-count">{{ AMCount(events) }}</span>&nbsp;
                                <span class="pm-count">{{ PMCount(events) }}</span>
                            </span>
                            <span class="vuecal__no-event" v-if="['week', 'day'].includes(view.id) && !events.length">
                                No WFH 👌
                            </span>
                        </template>
                    </VueCal>

                    <!-- Event Dialog -->
                    <v-dialog v-model="showDialog">
                        <v-card class="mycard">
                            <v-card-title style="background-color:#68B5C7;color:white;">
                                <strong>Employee List (ID - name)</strong>
                                <v-spacer />
                            </v-card-title>
                            <v-card-text>
                                <ul v-for="employee in selectedEvent.nameList" :key="employee.staff_id">
                                    <li>{{ employee.staff_id }} - {{ employee.name }}</li>
                                </ul>
                            </v-card-text>
                            <v-card-actions>
                                <v-spacer />
                                <v-btn text @click="showDialog = false">Close</v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>
                </div>
            </main>
        </MainLayout>
    </div>
</template>

<style scoped>
.mycard {
    min-width: 300px;
    max-width: 400px;
}
</style>