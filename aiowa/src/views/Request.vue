<template>
  <div class="max-w-6xl mx-auto p-6 bg-white shadow-md rounded-lg">
    <!-- Feedback message display -->
    <div v-if="feedbackMessage" :class="['p-4 rounded mb-4', feedbackType === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
      {{ feedbackMessage }}
    </div>

    <!-- Action buttons -->
    <div class="flex space-x-4 mb-4">
      <button @click="goToCreateRequestPage" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        Apply for WFH
      </button>
      <button @click="goToViewRequestStaffPage" class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
        View current & past requests
      </button>
    </div>

    <!-- Display requests in a table format -->
    <div v-if="requests && requests.length" class="overflow-x-auto">
      <h2 class="text-lg font-medium text-gray-700 mb-3">Requests</h2>
      <table class="min-w-full bg-white border border-gray-300 shadow rounded-lg">
        <thead>
          <tr class="bg-gray-100 border-b">
            <th class="px-4 py-2 text-left text-gray-600 font-semibold">Request ID</th>
            <th class="px-4 py-2 text-left text-gray-600 font-semibold">Staff ID</th>
            <th class="px-4 py-2 text-left text-gray-600 font-semibold">Reason</th>
            <th class="px-4 py-2 text-left text-gray-600 font-semibold">Status</th>
            <th class="px-4 py-2 text-left text-gray-600 font-semibold">Start Date</th>
            <th class="px-4 py-2 text-left text-gray-600 font-semibold">End Date</th>
            <th class="px-4 py-2 text-left text-gray-600 font-semibold">Time Slot</th>
            <th class="px-4 py-2 text-left text-gray-600 font-semibold">Request Type</th>
            <th class="px-4 py-2 text-left text-gray-600 font-semibold">Result Reason</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in requests" :key="request.request_id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-2 text-blue-600 underline cursor-pointer" @click.prevent="openRequestDetails(request.request_id)">
              {{ request.request_id }}
            </td>
            <td class="px-4 py-2 text-gray-700">{{ request.staff_id }}</td>
            <td class="px-4 py-2 text-gray-700">{{ request.reason }}</td>
            <td class="px-4 py-2 text-gray-700">{{ mapStatus(request.status) }}</td>
            <td class="px-4 py-2 text-gray-700">{{ request.startdate }}</td>
            <td class="px-4 py-2 text-gray-700">{{ request.enddate }}</td>
            <td class="px-4 py-2 text-gray-700">{{ mapTimeSlot(request.time_slot) }}</td>
            <td class="px-4 py-2 text-gray-700">{{ mapRequestType(request.request_type) }}</td>
            <td class="px-4 py-2 text-gray-700">{{ request.result_reason }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- No requests available message -->
    <div v-else class="text-gray-700 mt-4">No requests available.</div>

    <!-- Modal for displaying request details -->
    <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50">
      <div class="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
        <span class="absolute top-3 right-3 text-gray-600 cursor-pointer" @click="closeModal">&times;</span>
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Request Details</h2>

        <!-- Request Information -->
        <div class="mb-4">
          <p class="text-gray-700"><strong>Request ID:</strong> {{ selectedRequest.request_id }}</p>
          <p class="text-gray-700"><strong>Staff ID:</strong> {{ selectedRequest.staff_id }}</p>
          <p class="text-gray-700"><strong>Schedule ID:</strong> {{ selectedRequest.schedule_id }}</p>
          <p class="text-gray-700"><strong>Reason:</strong> {{ selectedRequest.reason }}</p>
          <p class="text-gray-700"><strong>Status:</strong> {{ mapStatus(selectedRequest.status) }}</p>
          <p class="text-gray-700"><strong>Start Date:</strong> {{ selectedRequest.startdate }}</p>
          <p class="text-gray-700"><strong>End Date:</strong> {{ selectedRequest.enddate }}</p>
          <p class="text-gray-700"><strong>Time Slot:</strong> {{ mapTimeSlot(selectedRequest.time_slot) }}</p>
          <p class="text-gray-700"><strong>Request Type:</strong> {{ mapRequestType(selectedRequest.request_type) }}</p>
        </div>

        <!-- Reason for Approval/Rejection -->
        <div class="mb-4">
          <p class="text-gray-700 font-medium">Reason for Approval/Rejection:</p>
          <textarea v-model="resultReason" rows="3" placeholder="Enter reason for approval/rejection" class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
        </div>

        <!-- Checkbox options for affected dates -->
        <div class="mb-4">
          <p class="text-gray-700 font-medium">Select Affected Dates:</p>
          <div v-for="date in affectedDates" :key="date" class="flex items-center space-x-2">
            <input type="checkbox" :value="date" v-model="selectedDates" class="form-checkbox text-blue-500">
            <label class="text-gray-700">{{ date }}</label>
          </div>
        </div>

        <!-- Approve and Reject buttons -->
        <div class="flex space-x-4">
          <button 
            class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600" 
            @click="approveRequest" 
            :disabled="!isApproveEnabled"
            :class="{ 'opacity-50 cursor-not-allowed': !isApproveEnabled }">Approve
          </button>
          <button 
            class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            @click="rejectRequest" 
            :disabled="!isRejectEnabled"
            :class="{ 'opacity-50 cursor-not-allowed': !isRejectEnabled }">Reject
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
const VITE_AWS_URL = import.meta.env.VITE_AWS_URL

export default {
  data() {
    return {
      requests: [], // Store all the fetched requests
      selectedRequest: {}, // Store details of the selected request
      showModal: false, // Show upon clicking into a specific request, by default hidden
      feedbackMessage: '', // Display message user feedback after approval/rejection
      feedbackType: '', // Message type: 'success' or 'error'
      resultReason: '', // Store the result_reason entered by the user
      affectedDates: [], // Store the list of all affected dates
      selectedDates: [], // Store the selected dates for approval
    };
  },
  computed: {
    // Determine if the Approve button should be enabled
    isApproveEnabled() {
      return this.selectedDates.length > 0 && this.resultReason.trim() !== '';
    },
    isRejectEnabled() {
      return this.resultReason.trim() !== '';
    }
  },
  methods: {
    // Method to calculate all dates between two dates
    calculateAffectedDates(startDate, endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      const dates = [];

      while (start <= end) {
        dates.push(new Date(start).toISOString().split('T')[0]); // Format as YYYY-MM-DD
        start.setDate(start.getDate() + 1);
      }

      return dates;
    },
    goToCreateRequestPage() {
      // Programmatic navigation to the Create New Request page
      this.$router.push({ name: 'newrequest' });
    },
    goToViewRequestStaffPage() {
      this.$router.push({ name: 'viewrequeststaff' });
    },
    async fetchRequestData() {
      console.log('Fetching requests...');
      console.log(this.access_token, this.staff_id);
      // Fetch request data for all of current user's team members
      try {
        const response = await axios.get(`${VITE_AWS_URL}/team/requests`, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.access_token}`,  // Include the access token here
            'X-Staff-ID': this.staff_id         // Include the staff ID here
          }
        });
        console.log('Request data received:', response.data);
        this.requests = response.data; // Store the list of requests
      } catch (error) {
        console.error("There was an error fetching the request data:", error);
      }
    },
    async openRequestDetails(requestId) {
      console.log(`Fetching details for request ID: ${requestId}`);
      // Fetch the details of the selected request from the server
      try {
        const response = await axios.get(`${VITE_AWS_URL}/request/${requestId}`, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.access_token}`,  // Include the access token here
          }
        });
        this.selectedRequest = response.data;
        this.affectedDates = this.calculateAffectedDates(this.selectedRequest.startdate, this.selectedRequest.enddate);
        this.selectedDates = []; // Reset selected dates for each request
        this.showModal = true; // Show the modal with request details
      } catch (error) {
        console.error("There was an error fetching the request details:", error);
      }
    },
    closeModal() {
      this.showModal = false; // Hide the modal
    },
    async approveRequest() {
      if (!this.isApproveEnabled) {
        console.error('Approve button should not be enabled when conditions are not met.');
        return; // Should not reach this point due to the disabled button
      }
      console.log(`Approving request ID: ${this.selectedRequest.request_id}`);
      // API Call to method for approval in backend
      try {
        const response = await axios.put(`${VITE_AWS_URL}/request/${this.selectedRequest.request_id}/approve`, {
          result_reason: this.resultReason,
          approved_dates: this.selectedDates
        }, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.access_token}`
          }
        });
        console.log('Request approved:', response.data);
        this.showModal = false;
        this.feedbackMessage = 'Request approved successfully!';
        this.feedbackType = 'success';
        this.refreshRequests();
        setTimeout(() => this.feedbackMessage = '', 3000);
      } catch (error) {
        console.error('Failed to approve request:', error);
        this.feedbackMessage = 'Failed to approve the request. Please try again.';
        this.feedbackType = 'error';
      }
    },
    async rejectRequest() {
      if (!this.isRejectEnabled) {
        console.error('Reject button should not be enabled when conditions are not met.');
        return; // Should not reach this point due to the disabled button
      }
      console.log(`Rejecting request ID: ${this.selectedRequest.request_id}`);
      // Send the result_reason with the rejection
      try {
        const response = await axios.put(`${VITE_AWS_URL}/request/${this.selectedRequest.request_id}/reject`, {
          result_reason: this.resultReason
        }, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.access_token}`
          }
        });
        console.log('Request rejected:', response.data);
        this.showModal = false;
        this.feedbackMessage = 'Request rejected successfully!';
        this.feedbackType = 'success';
        this.refreshRequests();
        setTimeout(() => this.feedbackMessage = '', 3000);
      } catch (error) {
        console.error('Failed to reject request:', error);
        this.feedbackMessage = 'Failed to reject the request. Please try again.';
        this.feedbackType = 'error';
      }
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
    },
    mapTimeSlot(timeSlot) {
      switch (timeSlot) {
        case 1:
          return 'AM';
        case 2:
          return 'PM';
        case 3:
          return 'AMPM';
      }
    },
    mapRequestType(requestType) {
      switch (requestType) {
        case 1:
          return 'Adhoc';
        case 2:
          return 'Recurring';
      }
    },
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
  margin: 10% auto; /* Reduced margin */
  padding: 30px; /* Increased padding */
  border: 1px solid #888;
  width: 60%; /* Adjusted width for better layout */
  border-radius: 8px; /* Rounded corners for modern look */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2); /* Subtle shadow for depth */
}

.request-info p {
  margin: 10px 0; /* Increased margin between paragraphs */
}

.result-reason {
  margin-top: 20px; /* Spacing above the result reason section */
}

.result-reason textarea {
  width: 100%; /* Full width for the textarea */
  margin-top: 5px; /* Space above the textarea */
  padding: 10px; /* Padding inside textarea */
  border: 1px solid #ccc; /* Subtle border */
  border-radius: 4px; /* Rounded corners */
}

.action-buttons {
  margin-top: 20px; /* Space above the buttons */
  display: flex;
  justify-content: space-between; /* Distribute space evenly */
}

.approve-button {
  padding: 10px 20px;
  background-color: #42b983; /* Green for approve */
  color: white;
  border: none;
  cursor: pointer;
  margin: 5px;
}

.approve-button.disabled {
  background-color: #cccccc; /* Light gray background */
  color: #666666; /* Darker gray text */
  cursor: not-allowed; /* Not allowed cursor */
}

.approve-button.disabled:hover {
  background-color: #cccccc; /* Prevent hover effect when disabled */
}

.reject-button {
  padding: 10px 20px;
  background-color: #d9534f; /* Red for reject */
  color: white;
  border: none;
  cursor: pointer;
  margin: 5px;
}

.reject-button.disabled {
  background-color: #cccccc; /* Light gray background */
  color: #666666; /* Darker gray text */
  cursor: not-allowed; /* Not allowed cursor */
}

.reject-button.disabled:hover {
  background-color: #cccccc; /* Prevent hover effect when disabled */
}

button {
  flex: 1; /* Equal size for buttons */
  margin: 0 5px; /* Spacing between buttons */
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
