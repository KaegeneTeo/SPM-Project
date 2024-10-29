<template>
  <div class="max-w-5xl mx-auto p-6 bg-white shadow-md rounded-lg">
    <h1 class="text-2xl font-semibold text-gray-800 mb-4">My Requests</h1>
    
    <div v-if="error" class="p-4 bg-red-100 text-red-700 rounded mb-4">{{ error }}</div>
    
    <div v-if="requests.length > 0">
      <h2 class="text-lg font-medium text-gray-700 mb-3">Requests for Staff ID: {{ staffId }}</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-300 shadow rounded-lg">
          <thead>
            <tr class="bg-gray-100 border-b border-gray-300">
              <th class="px-4 py-2 text-left text-gray-600 font-semibold">Request ID</th>
              <th class="px-4 py-2 text-left text-gray-600 font-semibold">Reason</th>
              <th class="px-4 py-2 text-left text-gray-600 font-semibold">Status</th>
              <th class="px-4 py-2 text-left text-gray-600 font-semibold">Start Date</th>
              <th class="px-4 py-2 text-left text-gray-600 font-semibold">End Date</th>
              <th class="px-4 py-2 text-left text-gray-600 font-semibold">Time Slot</th>
              <th class="px-4 py-2 text-left text-gray-600 font-semibold">Request Type</th>
              <th class="px-4 py-2 text-left text-gray-600 font-semibold">Action</th>
              <th class="px-4 py-2 text-left text-gray-600 font-semibold">W/C Reason</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="request in requests"
              :key="request.request_id"
              class="border-b hover:bg-gray-50"
            >
              <td class="px-4 py-2 text-gray-700">{{ request.request_id }}</td>
              <td class="px-4 py-2 text-gray-700">{{ request.reason }}</td>
              <td class="px-4 py-2 text-gray-700">{{ getStatusLabel(request.status) }}</td>
              <td class="px-4 py-2 text-gray-700">{{ request.startdate }}</td>
              <td class="px-4 py-2 text-gray-700">{{ request.enddate }}</td>
              <td class="px-4 py-2 text-gray-700">{{ getTimeSlotLabel(request.time_slot) }}</td>
              <td class="px-4 py-2 text-gray-700">{{ getRequestTypeLabel(request.request_type) }}</td>
              <td class="px-4 py-2">
                <button
                  v-if="request.status === 1"
                  @click="cancelRequest(request.request_id)"
                  class="px-3 py-1 text-sm text-white bg-red-500 rounded hover:bg-red-600"
                >
                  Withdraw
                </button>
                <button
                  v-if="request.status === 0"
                  @click="withdrawRequest(request.request_id)"
                  class="px-3 py-1 text-sm text-white bg-yellow-500 rounded hover:bg-yellow-600"
                >
                  Cancel
                </button>
              </td>
              <td class="px-4 py-2">
                <input type="text" class="p-2 border border-gray-300 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div v-else-if="requests.length === 0 && !error && showNoRecords" class="text-gray-700 mt-4">No records found for this staff ID.</div>
  </div>
</template>

<script>
import axios from "axios";
const VITE_AWS_URL = import.meta.env.VITE_AWS_URL;

export default {
  data() {
    return {
      staffId: localStorage.getItem('staff_id'),
      requests: [],
      error: null,
      showNoRecords: false,  // New flag to control the "No records" message
    };
  },
  methods: {
    getStaffId() {
      //axios.get(`http://127.0.0.1:5000/getstaffid`, {
      axios.get(`${VITE_AWS_URL}/getstaffid`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.access_token}`,  // Include the access token here
          'X-Staff-ID': this.staff_id          // Include the staff ID here 
        }
      })
      .then(response => {
        console.log(response.data);
        this.staffId = response.data.staff_id;
        this.fetchRequests();  // Fetch requests after staff ID is retrieved
      })
      .catch(error => {
        console.error("Error fetching staff ID:", error);
        this.error = "Failed to fetch staff ID.";
      });
    },
    async fetchRequests() {
      if (!this.staffId) {
        this.error = "Please enter a valid Staff ID.";
        return;
      }

      try {
        this.error = null;
        this.showNoRecords = false;  // Reset flag before fetching
        //const response = await axios.get(`http://127.0.0.1:5000/requests/${this.staffId}`, {
        const response = await axios.get(`${VITE_AWS_URL}/requests/${this.staffId}`, {
          headers: {
            'Authorization': `Bearer ${this.access_token}`,  // Include the access token
            'X-Staff-ID': this.staff_id                     // Include the staff ID here
          }
        });

        this.requests = response.data;
        console.log(response);

        // Only set showNoRecords to true if the response data is empty
        if (this.requests.length === 0) {
          this.showNoRecords = true;
        }
      } catch (err) {
        console.log(err);

        // If it's a 404 error, and contains the specific message
        if (err.response && err.response.status === 404) {
          this.showNoRecords = true;
        } else {
          this.error = "Error fetching data: " + (err.response?.data?.detail || err.message);
          this.requests = [];
        }
      }
    },
    getStatusLabel(status) {
      switch (status) {
        case 0:
          return "Pending";
        case 1:
          return "Approved";
        case -1:
          return "Rejected";
        default:
          return "Error";
      }
    },
    getTimeSlotLabel(timeSlot) {
      switch (timeSlot) {
        case 1:
          return "AM (9am - 1pm)";
        case 2:
          return "PM (2pm - 6pm)";
        case 3:
          return "Full Day (9am - 6pm)";
        default:
          return "Error";
      }
    },
    getRequestTypeLabel(requestType) {
      switch (requestType) {
        case 1:
          return "Adhoc";
        case 2:
          return "Recurring";
        default:
          return "Error";
      }
    },
    getButtonLabel(status) {
      switch (status) {
        case 0:
          return "Withdraw";
        case 1:
          return "Cancel";
        case -1:
          return "Rejected";
        default:
          return "Error";
      }
    },
    withdrawRequest(request_id){
      axios.delete(`${VITE_AWS_URL}/withdraw_request/${request_id}`)
      //axios.delete(`http://127.0.0.1:5000/withdraw_request/${request_id}`)
    .then(response => {
      console.log('Request withdrawn successfully:', response.data);
      alert('Request cancelled successfully!');
      location.reload()
    })
    .catch(error => {
      console.error('Error withdrawing request:', error);
      alert('Error withdrawing request');
    });
    },
    cancelRequest(request_id){
      axios.delete(`${VITE_AWS_URL}/cancel_request/${request_id}`)
      //axios.delete(`http://127.0.0.1:5000/cancel_request/${request_id}`)
    .then(response => {
      console.log('Request cancelled successfully:', response.data);
      alert('Request withdrawn successfully!');
      location.reload()
    })
    .catch(error => {
      console.error('Error cancelling request:', error);
      alert('Error cancelling request');
    });
    }
  },
  mounted() {
    this.staff_id = localStorage.getItem('staff_id');
    this.access_token = localStorage.getItem('access_token');
    this.getStaffId();  // Fetch the staff ID and then the requests
  }
};
</script>

<style scoped>
.error {
  color: red;
  margin-top: 10px;
}

table {
  margin-top: 20px;
  width: 100%;
  border-collapse: collapse;
}

table th, table td {
  padding: 8px;
  text-align: left;
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
input[type="text"] {
  border: 2px solid black;
  border-radius: 4px;
}
</style>
