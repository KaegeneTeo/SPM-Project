<script>
import MainLayout from "../components/MainLayout.vue"
import VueCal from 'vue-cal'
import 'vue-cal/dist/vuecal.css'
import axios from "axios";
import { compile, DeprecationTypes } from "vue";
const   VITE_AWS_URL = import.meta.env.VITE_AWS_URL



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
            selectedPosition: "",
            selectedReportingManager: "",
            managername: "",
            position:"",
            dept: ["CEO", "Consultancy", "Engineering", "Finance", "HR", "IT", "Sales", "Solutioning"],
            staff_id: null,
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
        this.staff_id = localStorage.getItem('staff_id');
        this.position = localStorage.getItem('position');
        if(this.role === '2'){
            this.search()
        }

    },
    watch: {
        selectedDept(newDept) {
            this.fetchTeams(newDept); // Fetch teams whenever the department changes
            this.selectedTeam = "";    // Reset the selected team
        },
        selectedTeam(newTeam){
            this.fetchTeamDetails(newTeam);
            
        }        
    },
    methods: {
        async fetchTeamDetails(team) {
            if(!team){
                return;
            }
            if(this.role == '1'){    
                if(team == 'all'){
                    this.selectedReportingManager = 'all'
                    return
                }
                this.managername = team.split("'")[0];
                // this.pos = team.split('(')[1].replace(")", "");
                
                const response = await axios.get(`${VITE_AWS_URL}/team_details`, {
                    params: {m_name : this.managername, dept : this.selectedDept}
                });
                this.selectedReportingManager = response.data["staff_id"]
                // console.log(this.selectedReportingManager)
            }
            else if(this.role == '3'){
                if(team == 'all'){
                    this.selectedReportingManager = this.staff_id
                    
                    // console.log(this.selectedReportingManager)
                }
                else if (team == 'my team'){
                    this.selectedReportingManager = localStorage.getItem('reporting_manager')
                    // console.log(this.selectedReportingManager)
                }
                
            }
            
        },
        async fetchTeams(department) {
            if (!department) {
                this.filteredTeams = []; // Clear teams if no department is selected
                return;
            }
            if(department == 'all'){
                
                this.selectedDept = 'all'
                this.filteredTeams = []
                return;
            }
            
            try {
                // Check if the selected department is "CEO"
                if (department === "CEO") {
                    // Make a request to fetch the CEO's team
                    const response = await axios.get(`${VITE_AWS_URL}/teams_by_reporting_manager`, {
                        params: { department }
                    });

                    // Assuming the response contains the CEO's information
                    console.log(response.data.teams[0].manager_name); // Access the first item in the response array

                    if (response) {
                        const ceoName = response.data.teams[0].manager_name; // Get CEO's name
                        console.log(ceoName)
                        const position = response.data.positions[0]; // Get CEO's position

                        // Create the team display string
                        this.filteredTeams = [`${ceoName}'s Team (${position})`];

                        // Optionally, you can append team members if needed
                        const teamMembers = response.data.positions[0].team.map(member => member.staff_fname);
                        this.filteredTeams.push(...teamMembers); // Add team members to the list
                    } else {
                        this.filteredTeams = []; // No teams available
                    }

                } else {
                    const response = await axios.get(`${VITE_AWS_URL}/teams_by_reporting_manager`, {
                        params: { department } // Pass department as a query parameter
                    });
                    console.log(response.data)
                    // Initialize with "All"
                    this.filteredTeams = [];

                    // Loop through the teams to build the formatted list, skipping the first item if needed
                    response.data.teams.slice(1).forEach(manager => { // Start from the second manager
                        const managerName = manager.manager_name;
                        manager.positions.forEach(positionGroup => {
                            const position = positionGroup.position;
                            this.filteredTeams.push(`${managerName}'s Team (${position})`); // Format team names
                        });
                    });
                }
            } catch (error) {
                console.error("Error fetching teams:", error);
            }
        },
        async search() {
            let params = {};
            
            if (this.role === '1') {
                if (this.selectedTeam == 'all' && this.selectedDept == 'all'){
                    params = {dept: 'all', reporting_manager: 'all', position :this.position, role: this.role}
                    // console.log(params)
                }
                else {
                    params = {dept: this.selectedDept, role: this.role, reporting_manager: this.selectedReportingManager, position: this.position}
                    // console.log(params);
                }
                
            }
            if (this.role === '3') {
                if (this.selectedTeam == 'all'){
                    params = {dept: localStorage.getItem('dept'), role: localStorage.getItem('role'), reporting_manager: this.selectedReportingManager, position: localStorage.getItem('position')}
                    // console.log(params)
                }
                else if (this.selectedTeam == 'my team'){
                    params = {dept: localStorage.getItem('dept'), role: this.role, reporting_manager: this.selectedReportingManager, position: this.position}
                    // console.log(params)
                }
            }
            if (this.role === '2'){
                params = {dept:localStorage.getItem('dept'), role : '3', position: 'Sales Manager', reporting_manager: localStorage.getItem('reporting_manager')}
            }    
            axios.get(`${VITE_AWS_URL}/schedules`, { params })
                .then(response => {
                    this.events = response.data['schedules'];
                    console.log(this.events)
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
                            <option value="all">All</option>
                            <option v-for="item in dept" :key="item" :value="item">{{ item }}</option>
                        </select>
                    </div>
                    <div class="mt-4">
                        <label for="schedule-selector-team" class="block text-sm font-medium text-gray-700">Select Team:</label>
                        <select v-model="selectedTeam" id="schedule-selector-team" class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                            <option value="">Select a team</option>
                            <option value="all">All</option>
                            <option v-for="item in filteredTeams" :key="item">
                                {{ item }}
                            </option>
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
                            <option value="all">All</option>
                            <option value="my team">My Team</option>
                            
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
                <div class="col-span-12 lg:col-span-6">
                    <VueCal class="vuecal--blue-theme" style="height: 500px;" :events="events" :hide-weekends="true" events-count-on-year-view :on-event-click="onEventClick" :time-from="9 * 60" :time-to="18 * 60">
                        <template #cell-content="{ cell, view, goNarrower, events }">
                            <span class="vuecalcell-date" :class="view.id" @click="goNarrower">
                                <span class="clickable">{{ cell.content }}</span>
                            </span>
                            <span class="vuecalcell-events-count " v-if="['years', 'year', 'month'].includes(view.id) && events.length">
                                <span style="background-color:#FFA500; color: white; " class="am-count px-2 h-4 w-4 rounded-full">{{ AMCount(events) }}</span>&nbsp;
                                <span style="background-color:#9C27B0; color: white; " class="pm-count px-2 h-4 w-4 rounded-full">{{ PMCount(events) }}</span>
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
                                <span>WFH</span> 
                                <ul v-for="employee in selectedEvent.WFH"> 
                                    <li>{{ employee }}</li> 
                                </ul> 
                                
                                <span>In Office</span> 
                                <ul v-for="employee in selectedEvent.inOffice"> 
                                    <li>{{ employee }}</li> 
                                </ul> 
                            </v-card-text>
                            <v-card-actions>
                                <v-spacer />
                                <v-btn text @click="showDialog = false">Close</v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>
                </div>

                <!-- Right column: Legend --> 
                <div class="col-span-12 lg:col-span-3"> 
                    <h2 class="text-lg font-semibold text-gray-900">Legend</h2> 
                    <ul class="mt-2 space-y-1"> 
                        <li class="flex items-center"> 
                            <span class="inline-block h-4 w-4 rounded-full mr-2" 
                                style="background-color:#FFA500;"></span> AM 
                        </li> 
                        <li class="flex items-center"> 
                            <span class="inline-block h-4 w-4 rounded-full mr-2" 
                                style="background-color:#9C27B0;"></span> PM 
                        </li> 
                    </ul> 
                </div>
            </main>
        </MainLayout>
    </div>
</template>

<style scoped>
#app {
    margin: 30px auto;
    max-width: 580px;
    height: 350px;
}

.vuecalevent {
    background-color: rgba(173, 216, 230, 0.5);
}

.vuecalbody .clickable {
    color: #4682b4;
    text-decoration: underline;
}

.vuecal__cell-date {
    display: inline-block;
}

.am-count {
    background-color: #FFA500;
    height: 100%;
    min-width: 12px;
    padding: 0 3px;
    border-radius: 12px;
    display: inline;
    color: white;
}

.pm-count {
    background-color: #9C27B0;
    height: 100%;
    min-width: 12px;
    padding: 0 3px;
    border-radius: 12px;
    display: inline;
    color: white;
}

.vuecal__cell-events-count {
    background: transparent;
}

.mycard {
    margin: auto;
}
</style>
<style>
.vuecal__event.AM {
    background-color: #FFA500;
    border: 1px solid rgb(233, 136, 46);
    color: #fff;
}

.vuecal__event.PM {
    background-color: #9C27B0;
    border: 1px solid #801f91;
    color: #fff;
}

.vuecal__event {
    cursor: pointer;
}

.vuecal__event-title {
    font-size: 1.2em;
    font-weight: bold;
    margin: 4px 0 8px;
}

.vuecal__event-time {
    display: inline-block;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.2);
}

.vuecal__event-content {
    font-style: italic;
}
</style>