<script>
import MainLayout from "../components/MainLayout.vue"
import VueCal from 'vue-cal'
import 'vue-cal/dist/vuecal.css'

export default {
    components: {
        VueCal // Registering the component
    },
    methods: {
        AMCount(events) {
            var AM = 0
            if (events.length >= 1) {
                for (var i = 0; i < events.length; i++) {
                    if (events[i].class === "AM") {
                        AM += events[i].count
                    }
                }
            }
            return AM
        },
        PMCount(events) {
            var PM = 0
            if (events.length >= 1) {
                for (var i = 0; i < events.length; i++) {
                    if (events[i].class === "PM") {
                        PM += events[i].count
                    }
                }
            }
            return PM
        },
        // customCount:events =>  {
        //     var AM = 0
        //     var PM = 0
        //     if (events.length >= 1) {
        //         for (var i = 0; i < events.length; i++) {
        //             if (events[i].class === "AM") {
        //                 AM += events[i].count
        //             }
        //             if (events[i].class === "PM") {
        //                 PM += events[i].count
        //             }
        //         }
        //     }
        //     return `${AM} AM, ${PM} PM`
        // },
        onEventClick(event, e) {
            this.selectedEvent = event
            this.showDialog = true

            // Prevent navigating to narrower view (default vue-cal behavior). 
            e.stopPropagation()
        }
    },
    data() {
        return {
            selectedEvent: {},
            showDialog: false,
            events: [
                {
                    start: '2024-09-19 09:00',
                    end: '2024-09-19 13:00',
                    title: '1',
                    class: 'AM',
                    count: 1,
                    nameList: [
                        {
                            ID: 0,
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
                            ID: 3,
                            name: "Bob"
                        },
                        {
                            ID: 4,
                            name: "Alice"
                        },
                        {
                            ID: 1,
                            name: "Jane"
                        }
                    ]
                }
            ]
        }
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
                    <label for="schedule-selector" class="block text-sm font-medium text-gray-700">Select
                        Schedule:</label>
                    <select id="schedule-selector"
                        class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                        <option>Schedule 1</option>
                        <option>Schedule 2</option>
                        <option>Schedule 3</option>
                    </select>
                </div>

                <!-- Middle column: VueCal Calendar -->
                <div class="col-span-12 lg:col-span-6">
                    <VueCal class="vuecal--blue-theme " style="height:500px;" :events="events" :hide-weekends="true"
                        events-count-on-year-view :on-event-click="onEventClick" :time-from="9 * 60" :time-to="18 * 60">
                        <template #cell-content="{ cell, view, goNarrower, events }">
                            <span class="vuecalcell-date" :class="view.id" @click="goNarrower">
                                <span class="clickable">{{ cell.content }}</span>

                            </span>
                            <span class="vuecalcell-events-count"
                                v-if="['years', 'year', 'month'].includes(view.id) && events.length">
                                <span class="am-count">{{ AMCount(events) }}</span>&nbsp;
                                <span class="pm-count">{{ PMCount(events) }}</span>
                            </span>
                            <span class="vuecal__no-event" v-if="['week', 'day'].includes(view.id) && !events.length">
                                No WFH 👌
                            </span>
                        </template>
                    </VueCal>
                    <v-dialog v-model="showDialog">
                        <v-card class = "mycard">
                            <v-card-title style="background-color:#68B5C7;color:white;">
                                <strong>Employee List (ID - name)</strong>
                                <v-spacer />
                            </v-card-title>
                            <v-card-text>
                                <ul v-for="employee in selectedEvent.nameList">
                                    <li>
                                        {{ employee.ID }} - {{ employee.name }}
                                    </li>
                                </ul>
                            </v-card-text>
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
    margin:auto;
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