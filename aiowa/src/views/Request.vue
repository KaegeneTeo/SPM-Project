
<template>
    <div>
      <button @click="goToCreateRequestPage">Apply for WFH</button>
    </div>
  </template>
  
  <script>
  export default {
    methods: {
      goToCreateRequestPage() {
        // Programmatic navigation to the Create New Request page
        this.$router.push({ name: 'newrequest' });
      },
    },
  };
  </script>
  
  <style scoped>
  button {
    padding: 10px 20px;
    background-color: #42b983;
    color: white;
    border: none;
    cursor: pointer;
  }
  </style>