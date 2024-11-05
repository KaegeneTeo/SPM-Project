<template>
    <div class="max-w-xl mx-auto mt-10 p-6 bg-white shadow-md rounded-lg">
        <h1 class="text-2xl font-semibold text-gray-800 mb-4">New Request</h1>
        <form @submit.prevent="submitRequest" class="space-y-6">
            <div>
                <label for="reason" class="block text-sm font-medium text-gray-700">Reason:</label>
                <textarea
                    v-model="form.reason"
                    id="reason"
                    required
                    class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    rows="4"></textarea>
            </div>
            <div>
                <label for="startdate" class="block text-sm font-medium text-gray-700">Start Date:</label>
                <input
                    type="date"
                    v-model="form.startdate"
                    :min="minDate"
                    @change="handleStartDateChange"
                    id="startdate"
                    required
                    class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
                <p v-if="dateError" class="text-red-500 text-xs mt-1">{{ dateError }}</p>
            </div>
            <div>
                <label for="enddate" class="block text-sm font-medium text-gray-700">End Date:</label>
                <input
                    type="date"
                    v-model="form.enddate"
                    :min="form.startdate || minDate"
                    @change="validateEndDate"
                    id="enddate"
                    required
                    class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
                <p v-if="endDateError" class="text-red-500 text-xs mt-1">{{ endDateError }}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Time Slot:</label>
                <div class="mt-2 space-y-1">
                    <div class="flex items-center">
                        <input
                            type="radio"
                            id="morning"
                            value="1"
                            v-model="form.time_slot"
                            :disabled="!canChooseAM"
                            class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300" />
                        <label for="morning" class="ml-2 block text-sm text-gray-700">AM WFH (9AM - 1PM)</label>
                    </div>
                    <div class="flex items-center">
                        <input
                            type="radio"
                            id="afternoon"
                            value="2"
                            v-model="form.time_slot"
                            :disabled="!canChoosePM"
                            class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300" />
                        <label for="afternoon" class="ml-2 block text-sm text-gray-700">PM WFH (2PM - 6PM)</label>
                    </div>
                    <div class="flex items-center">
                        <input
                            type="radio"
                            id="evening"
                            value="3"
                            v-model="form.time_slot"
                            :disabled="!canChooseFullDay"
                            class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300" />
                        <label for="evening" class="ml-2 block text-sm text-gray-700">Full Day WFH (9AM - 6PM)</label>
                    </div>
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Request Type:</label>
                <div class="mt-2 space-y-1">
                    <div class="flex items-center">
                        <input
                            type="radio"
                            id="type1"
                            value="1"
                            v-model="form.request_type"
                            class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300" />
                        <label for="type1" class="ml-2 block text-sm text-gray-700">Adhoc</label>
                    </div>
                    <div class="flex items-center">
                        <input
                            type="radio"
                            id="type2"
                            value="2"
                            v-model="form.request_type"
                            class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300" />
                        <label for="type2" class="ml-2 block text-sm text-gray-700">Recurring</label>
                    </div>
                </div>
            </div>
            <button
                type="submit"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                Submit Request
            </button>
        </form>

        <div v-if="message" class="mt-4 p-2 bg-green-100 text-green-700 rounded">
            <p>{{ message }}</p>
        </div>
    </div>
</template>

<script>
import axios from "axios";
const VITE_AWS_URL = import.meta.env.VITE_AWS_URL;

export default {
    data() {
        return {
            form: {
                staffid: localStorage.getItem("staff_id"),
                reason: "",
                status: 0,
                startdate: "",
                enddate: "",
                time_slot: null,
                request_type: null,
            },
            message: null,
            minDate: this.getCurrentDate(),
            dateError: null,
            endDateError: null,
            canChooseAM: true,
            canChoosePM: true,
            canChooseFullDay: true,
        };
    },
    methods: {
        getStaffId() {
            //axios.get(`http://127.0.0.1:5000/getstaffid`, {
            axios
                .get(`${VITE_AWS_URL}/getstaffid`, {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${this.access_token}`, // Include the access token here
                        "X-Staff-ID": this.staff_id, // Include the staff ID here
                    },
                })
                .then((response) => {
                    this.form.staffid = response.data.staff_id;
                })
                .catch((error) => {
                    console.error("Error fetching staff ID:", error);
                });
        },
        getCurrentDate() {
            const today = new Date();
            return today.toISOString().split("T")[0]; // Format as YYYY-MM-DD
        },
        isWeekend(date) {
            const day = new Date(date).getDay();
            return day === 0 || day === 6; // 0 is Sunday, 6 is Saturday
        },
        handleStartDateChange() {
            const selectedDate = new Date(this.form.startdate);
            const currentDate = new Date(this.getCurrentDate());

            // Check if the selected date is a weekend
            if (this.isWeekend(this.form.startdate)) {
                this.dateError = "Weekends are not allowed. Please select a weekday.";
                this.form.startdate = ""; // Clear the start date if it's a weekend
                return;
            }

            this.dateError = null; // Clear any previous error

            // Reset time slot options
            this.canChooseAM = true;
            this.canChoosePM = true;
            this.canChooseFullDay = true;
            this.endDateError = null; // Reset end date error

            if (selectedDate.getTime() === currentDate.getTime()) {
                const currentTime = new Date();

                const nineAM = new Date();
                nineAM.setHours(9, 0, 0, 0); // 9:00:00 AM

                const twoPM = new Date();
                twoPM.setHours(14, 0, 0, 0); // 2:00:00 PM

                if (currentTime >= nineAM && currentTime < twoPM) {
                    this.canChooseAM = false; // Disable AM if it's after 9:00:00 AM but before 2:00:00 PM
                }

                if (currentTime >= twoPM) {
                    this.canChooseAM = false;
                    this.canChoosePM = false; // Disable AM and PM if it's after 2:00:00 PM
                    this.form.startdate = ""; // Reset start date if it's today and after 2 PM
                    alert("You cannot select today as the start date after 2 PM.");
                }

                if (currentTime >= nineAM) {
                    this.canChooseFullDay = false; // Disable Full Day if it's after 9:00:00 AM
                }
            }
        },
        validateEndDate() {
            const currentDate = new Date(this.getCurrentDate());
            const selectedEndDate = new Date(this.form.enddate);
            if (selectedEndDate.getTime() != currentDate.getTime()) {
                this.canChooseAM = true;
                this.canChoosePM = true;
                this.canChooseFullDay = true;
                this.endDateError = null; // Reset end date error
            } else {
                this.handleStartDateChange();
            }

            if (this.form.enddate < this.form.startdate) {
                this.endDateError = "End date cannot be earlier than start date.";
            } else if (this.isWeekend(this.form.enddate)) {
                this.endDateError = "Weekends are not allowed. Please select a weekday.";
                this.form.enddate = ""; // Clear the end date if it's a weekend
            } else {
                this.endDateError = null;
            }
        },
        async submitRequest() {
            if (this.endDateError || this.dateError) {
                alert("Please correct the form before submitting.");
                return;
            }

            try {
                //const response = await axios.post(`http://127.0.0.1:5000/requests/`, this.form, {
                const response = await axios.post(`${VITE_AWS_URL}/requests/`, this.form, {
                    headers: {
                        Authorization: `Bearer ${this.access_token}`, // Include the access token
                        "X-Staff-ID": this.staff_id, // Include the staff ID here
                    },
                });
                alert("Request created successfully!");
                this.$router.push({ name: "viewrequeststaff" });
            } catch (error) {
                if (error.response) {
                    console.error(error.response.data);
                    this.message = `Error: please fill in all fields.`;
                } else {
                    this.message = "An error occurred. Please try again.";
                }
            }
        },
    },
    mounted() {
        this.staff_id = localStorage.getItem("staff_id");
        this.access_token = localStorage.getItem("access_token");
        this.getStaffId();
    },
};
</script>

<style scoped>
/* Simple styles for form layout */
form div {
    margin-bottom: 10px;
}
button {
    padding: 8px 12px;
    background-color: #42b983;
    color: white;
    border: none;
    cursor: pointer;
}
input[type="number"],
textarea {
    width: 100%;
    padding: 8px;
    border: 2px solid black;
    border-radius: 4px;
    box-sizing: border-box;
    margin-top: 4px;
    margin-bottom: 10px;
}
.error {
    color: red;
    font-weight: bold;
}
</style>
