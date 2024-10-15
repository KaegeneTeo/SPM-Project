<template>
  <div>
    <h1><strong>My Requests</strong></h1>
    <br>
    
    
    <button @click="fetchRequests">Fetch Requests</button>
    
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="requests.length > 0">
      <h2>Requests for Staff ID: {{ staffId }}</h2>
      <table border="1">
        <thead>
          <tr>
            <th>Request ID</th>
            <th>Reason</th>
            <th>Status</th>
            <th>Start Date</th>
            <th>End Date</th>
            <th>Time Slot</th>
            <th>Request Type</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in requests" :key="request.request_id">
            <td>{{ request.request_id }}</td>
            <td>{{ request.reason }}</td>
            <td>{{ getStatusLabel(request.status) }}</td>
            <td>{{ request.startdate }}</td>
            <td>{{ request.enddate }}</td>
            <td>{{ getTimeSlotLabel(request.time_slot) }}</td>
            <td>{{ getRequestTypeLabel(request.request_type) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="requests.length === 0 && !error && showNoRecords">No records found for this staff ID.</div>
  </div>
</template>

<script>
import axios from "axios";
import { ENDPOINT_URL } from "../config/config.js";
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
      axios.get(`http://127.0.0.1:5000/getstaffid`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.access_token}`,  // Include the access token here
          'X-Staff-ID': this.staff_id          // Include the staff ID here 
        }
      })
    .then(response => {
      console.log(response.data);
      return response.data.staff_id
    })
    },
    async fetchRequests() {
      if (!this.staffId) {
        this.error = "Please enter a valid Staff ID.";
        return;
      }

      try {
        this.error = null;
        this.showNoRecords = false;  // Reset flag before fetching

        const response =  await axios.get(`http://127.0.0.1:5000/requests/${this.staffId}`);
        this.requests = response.data;
        console.log(response);
        // Only set showNoRecords to true if the response data is empty
        if (this.requests.length === 0) {
          this.showNoRecords = true;
        }
      } catch (err) {
        // If it's a 404 error, and contains the specific message
        console.log(err)
        if (err.status === 404) {
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
    }
  },
  mounted() {
    this.staff_id = localStorage.getItem('staff_id');
    this.access_token = localStorage.getItem('access_token');
    this.getStaffId();
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
</style>
