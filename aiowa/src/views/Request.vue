<template>
  <div>
    <!-- Feedback message display -->
    <div v-if="feedbackMessage" :class="['feedback', feedbackType]">
      {{ feedbackMessage }}
    </div>
    <button @click="goToCreateRequestPage">Apply for WFH</button>
    <br>
    <button @click="goToViewRequestStaffPage">View current & past requests</button>

    <!-- Display requests in a table format -->
    <div v-if="requests && requests.length">
      <h2>Requests</h2>
      <table>
        <thead>
          <tr>
            <th>Request ID</th>
            <th>Staff ID</th>
            <th>Reason</th>
            <th>Status</th>
            <th>Start Date</th>
            <th>End Date</th>
            <th>Time Slot</th>
            <th>Request Type</th>
          </tr>
        </thead>
        <tbody>
          <!-- For loop to display all request records -->
          <tr v-for="request in requests" :key="request.request_id">
            <td><a href="#" @click.prevent="openRequestDetails(request.request_id)">{{ request.request_id }}</a></td>
            <td>{{ request.staff_id }}</td>
            <td>{{ request.reason }}</td>
            <td>{{ mapStatus(request.status) }}</td> <!-- Status based on integer value -->
            <td>{{ request.startdate }}</td>
            <td>{{ request.enddate }}</td>
            <td>{{ request.time_slot }}</td>
            <td>{{ request.request_type }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- If there are no requests for this team -->
    <div v-else>
      <p>No requests available.</p>
    </div>

    <!-- Modal for displaying request details -->
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeModal">&times;</span>
        <h2>Request Details</h2>
        <p><strong>Request ID:</strong> {{ selectedRequest.request_id }}</p>
        <p><strong>Staff ID:</strong> {{ selectedRequest.staff_id }}</p>
        <p><strong>Schedule ID:</strong> {{ selectedRequest.schedule_id }}</p>
        <p><strong>Reason:</strong> {{ selectedRequest.reason }}</p>
        <p><strong>Status:</strong> {{ mapStatus(selectedRequest.status) }}</p> <!-- Status based on integer value -->
        <p><strong>Start Date:</strong> {{ selectedRequest.startdate }}</p>
        <p><strong>End Date:</strong> {{ selectedRequest.enddate }}</p>
        <p><strong>Time Slot:</strong> {{ selectedRequest.time_slot }}</p>
        <p><strong>Request Type:</strong> {{ selectedRequest.request_type }}</p>

        <!-- Approve and Reject buttons -->
        <button @click="approveRequest">Approve</button>
        <button @click="rejectRequest">Reject</button>
      </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios';


// console.log(staff_id)
export default {
  data() {
    return {
      requests: [], // Store all the fetched requests
      selectedRequest: {}, // Store details of the selected request
      showModal: false, // Show upon clicking into a specific request, by default hidden
      feedbackMessage: '', // Display message user feedback after approval/rejection
      feedbackType: '' // Message type: 'success' or 'error'
    };
  },
  methods: {
    goToCreateRequestPage() {
      // Programmatic navigation to the Create New Request page
      this.$router.push({ name: 'newrequest' });
    },
    goToViewRequestStaffPage() {
      this.$router.push({ name: 'viewrequeststaff' });
    },
    fetchRequestData() {
      console.log('Fetching requests...');
      console.log(this.access_token,this.staff_id)
      // Fetch request data for all of current user's team members
      axios.get('http://localhost:5000/team/requests', {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.access_token}`,  // Include the access token here
            'X-Staff-ID': this.staff_id          // Include the staff ID here 
          }
        })
        .then(response => {
          console.log('Request data received:', response.data);
          this.requests = response.data; // Store the list of requests
        })
        .catch(error => {
          console.error("There was an error fetching the request data:", error);
        });
    },
    openRequestDetails(requestId) {
      console.log(`Fetching details for request ID: ${requestId}`);
      // Fetch the details of the selected request from the server
      axios.get(`http://localhost:5000/request/${requestId}`, { withCredentials: true })
        .then(response => {
          this.selectedRequest = response.data;
          this.showModal = true; // Show the modal with request details
        })
        .catch(error => {
          console.error("There was an error fetching the request details:", error);
        });
    },
    closeModal() {
      this.showModal = false; // Hide the modal
    },
    approveRequest() {
      console.log(`Approving request ID: ${this.selectedRequest.request_id}`);
      // API Call to method for approval in backend
      axios.post(`http://localhost:5000/request/${this.selectedRequest.request_id}/approve`, { withCredentials: true })
        .then(response => {
          console.log('Request approved:', response.data);
          this.showModal = false; // Close the modal

          // Display success message
          this.feedbackMessage = 'Request approved successfully!';
          this.feedbackType = 'success';
          
          // Refresh list of requests
          this.refreshRequests();
          
          // Message auto clears after 3 seconds
          setTimeout(() => {
            this.feedbackMessage = '';
          }, 3000);
        })
        .catch(error => {
          console.error("There was an error approving the request:", error);
          // Display error message
          this.feedbackMessage = 'Failed to approve the request. Please try again.';
          this.feedbackType = 'error';
        });
    },
    rejectRequest() {
      console.log(`Rejecting request ID: ${this.selectedRequest.request_id}`);
      // API Call to method for rejection in backend
      axios.post(`http://localhost:5000/request/${this.selectedRequest.request_id}/reject`, { withCredentials: true })
        .then(response => {
          console.log('Request rejected:', response.data);
          this.showModal = false; // Close the modal

          // Display success message
          this.feedbackMessage = 'Request rejected successfully!';
          this.feedbackType = 'success';
          
          // Refresh list of requests
          this.refreshRequests();
          
          // Message auto clears after 3 seconds
          setTimeout(() => {
            this.feedbackMessage = '';
          }, 3000);
        })
        .catch(error => {
          console.error("There was an error rejecting the request:", error);
          // Display error message
          this.feedbackMessage = 'Failed to reject the request. Please try again.';
          this.feedbackType = 'error';
        });
    },
    refreshRequests() {
      // Fetch the latest list of requests after approval/rejection
      this.fetchRequestData();
    },
    mapStatus(status) {
      // Map integer status to respective strings
      switch(status) {
        case 1:
          return 'Approved';
        case -1:
          return 'Rejected';
        default:
          return 'Pending';
      }
    }
  },
  mounted() {
    console.log('Component mounted, fetching data...');
    this.access_token = localStorage.getItem('access_token');
    this.staff_id = localStorage.getItem('staff_id');
    // Fetch the request data when the component is mounted
    this.fetchRequestData();
  }
};

</script>


<style scoped>
button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  margin-bottom: 20px;
}

h2 {
  color: #42b983;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

table, th, td {
  border: 1px solid #dddddd;
}

th, td {
  text-align: left;
  padding: 8px;
}

th {
  background-color: #42b983;
  color: white;
}

td {
  background-color: #f9f9f9;
}

p {
  font-size: 16px;
}

.modal {
  display: block;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: 15% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 80%;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: black;
  text-decoration: none;
  cursor: pointer;
}

button {
  padding: 10px 20px;
  margin: 5px;
}

.feedback {
  padding: 10px;
  margin: 20px 0;
  border-radius: 5px;
  font-size: 16px;
  text-align: center;
}

.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
