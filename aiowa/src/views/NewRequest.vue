<template>
    <div>
      <h1><strong>New Request</strong></h1>
      <br>
      <form @submit.prevent="submitRequest">
        <div>
          <label for="staff_id">Staff ID:</label>
          <input type="number" v-model="form.staff_id" id="staff_id" required />
        </div>
        <div>
          <label for="reason">Reason:</label>
          <textarea v-model="form.reason" id="reason" required></textarea>
        </div>
        <div>
          <label for="date">Start Date:</label>
          <input type="date" v-model="form.startdate" id="startdate" required />
        </div>
        <div>
          <label for="date">End Date:</label>
          <input type="date" v-model="form.enddate" id="enddate" required />
        </div>
        <div>
        <label>Time Slot:</label>
        <div>
          <input type="radio" id="morning" value="1" v-model="form.time_slot" />
          <label for="morning">AM WFH(9AM - 1PM)</label>
        </div>
        <div>
          <input type="radio" id="afternoon" value="2" v-model="form.time_slot" />
          <label for="afternoon">PM WFH(2PM - 6PM)</label>
        </div>
        <div>
          <input type="radio" id="evening" value="3" v-model="form.time_slot" />
          <label for="evening">Full Day WFH(9AM - 6PM)</label>
        </div>
      </div>
      <div>
        <label>Request Type:</label>
        <div>
          <input type="radio" id="type1" value="1" v-model="form.request_type" />
          <label for="type1">Adhoc</label>
        </div>
        <div>
          <input type="radio" id="type2" value="2" v-model="form.request_type" />
          <label for="type2">Recurring</label>
        </div>
      </div>
        <button type="submit">Submit Request</button>
      </form>
  
      <div v-if="message">
        <p>{{ message }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        form: {
          staff_id: null,
          reason: "",
          status: 0,
          startdate: "",
          enddate: "",
          time_slot: null,
          request_type: null,
        },
        message: null,
      };
    },
    methods: {
      async submitRequest() {
        try {
          // Make the POST request to the FastAPI endpoint
          const response = await axios.post("http://127.0.0.1:8000/requests/", this.form);
          this.message = "Request created successfully!";
          console.log(response.data);  // You can inspect the response if needed
        } catch (error) {
          if (error.response) {
            // Server responded with an error status
            this.message = `Error: ${error.response.data.detail}`;
          } else {
            this.message = "An error occurred. Please try again.";
          }
        }
      },
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
  input[type=number], textarea {
  width: 100%;
  padding: 8px;
  border: 2px solid black;
  border-radius: 4px;
  box-sizing: border-box;
  margin-top: 4px;
  margin-bottom: 10px;
}
  </style>
  