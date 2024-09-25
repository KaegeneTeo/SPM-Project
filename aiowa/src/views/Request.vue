<template>
  <div>
    <button @click="goToCreateRequestPage">Apply for WFH</button>

    <!-- Display requests in a table format -->
    <div v-if="requests && requests.length">
      <h2>Requests</h2>
      <table>
        <thead>
          <tr>
            <th>Request ID</th>
            <th>Staff ID</th>
            <th>Schedule ID</th>
            <th>Reason</th>
            <th>Status</th>
            <th>Date</th>
            <th>Time Slot</th>
            <th>Request Type</th>
          </tr>
        </thead>
        <tbody>
          <!-- For loop to display all request records -->
          <tr v-for="request in requests" :key="request.request_id">
            <td>{{ request.request_id }}</td>
            <td>{{ request.staff_id }}</td>
            <td>{{ request.schedule_id }}</td>
            <td>{{ request.reason }}</td>
            <td>{{ request.status }}</td>
            <td>{{ request.date }}</td>
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
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      requests: [] // Store all the fetched requests
    };
  },
  methods: {
    goToCreateRequestPage() {
      // Programmatic navigation to the Create New Request page
      this.$router.push({ name: 'newrequest' });
    },
    fetchRequestData() {
      console.log('Fetching requests...');
      // Fetch request data for all of current user's team members
      axios.get(`/team/requests`) 
        .then(response => {
          console.log('Request data received:', response.data.requests);
          this.requests = response.data; // Store the list of requests
          console.log(response.data);
        })
        .catch(error => {
          console.error("There was an error fetching the request data:", error);
        });
    }
  },
  mounted() {
    console.log('Component mounted, fetching data...');
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
</style>
