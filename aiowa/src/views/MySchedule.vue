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
            reporting_manager:"",
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
        this.dept = localStorage.getItem('dept');
        this.reporting_manager = localStorage.getItem('reporting_manager')
        this.search()
        

    },
    methods: {
        async search() {
            // Retrieve the staff_id from local storage
            const staff_id = localStorage.getItem('staff_id');
            
            if (!staff_id) {
                alert("Staff ID not found in local storage. Please log in again.");
                return;
            }

            // Query using the staff_id to fetch personal schedules
            const params = { staff_id: this.staff_id, dept: this.dept, position: this.position, reporting_manager:this.reporting_manager };

            // Making an API call to the Supabase function or backend to fetch schedules
            try {
                const response = await axios.get(`${VITE_AWS_URL}/schedules`, { params });
                this.events = response.data['schedules'];
                
                if (this.events.length === 0) {
                    // Show a popup when no schedules are found
                    alert("There are no personal schedules found.");
                } else {
                    console.log(this.events);
                }
            } catch (error) {
                console.error("Error fetching personal schedules: ", error);
            }
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
                    <h1 class="text-3xl font-bold tracking-tight text-gray-900">My Schedules</h1>                                                     <!--FOR FILTERS, ONLY TEST WITH DEPT:SALES,CEO,HR-->
                </div>
            </header>

            <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 grid grid-cols-12 gap-4">
                <div class="col-span-12 lg:col-span-3"></div>

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
                                <strong>Employee List</strong>
                                <v-spacer />
                            </v-card-title>
                            <v-card-text> 
                                <strong>WFH</strong>
                                <table class="table table-bordered table-hover">
                                    <thead>
                                        <tr>
                                            <th scope="col">Staff_ID</th>
                                            <th scope="col">Name</th>
                                            <th scope="col">Dept</th>
                                            <th scope="col">Position</th>
                                        </tr>
                                    </thead>
                                    <tbody v-for="employee in selectedEvent.WFH">
                                        <tr>
                                            <th scope="row">{{employee.staff_id}}</th>
                                            <td>{{employee.staff_fname +" "+ employee.staff_lname}}</td>
                                            <td>{{ employee.dept }}</td>
                                            <td>{{ employee.position }}</td>
                                        </tr>
                                    </tbody>
                                </table>
                                <strong>In Office</strong>
                                <table class="table table-bordered table-hover">
                                    <thead>
                                        <tr>
                                            <th scope="col">Staff_ID</th>
                                            <th scope="col">Name</th>
                                            <th scope="col">Dept</th>
                                            <th scope="col">Position</th>
                                        </tr>
                                    </thead>
                                    <tbody v-for="employee in selectedEvent.inOffice">
                                        <tr>
                                            <th scope="row">{{employee.staff_id}}</th>
                                            <td>{{employee.staff_fname +" "+ employee.staff_lname}}</td>
                                            <td>{{ employee.dept }}</td>
                                            <td>{{ employee.position }}</td>
                                        </tr>
                                    </tbody>
                                </table>
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
th{
    text-align:left;
    padding-left: 10px;
    padding-right: 10px;
}
td{
    padding-left: 10px;
    padding-right: 10px;
}
.table-bordered th, .table-bordered td { border: 1px solid #48bc84!important }
</style>