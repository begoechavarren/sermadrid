<template>
  <div class="home">
    <h1>{{ msg }}</h1>
    <p>Select the location and time where you would<br>like to park in the Madrid SER zone</p>
    <!-- Form for datetime, latitude, and longitude inputs -->
    <form @submit.prevent="getItem" class="availability-form">
      <div class="form-group">
        <label for="datetimeInput">Datetime:</label>
        <input type="text" id="datetimeInput" v-model="datetime" placeholder="Enter datetime">
      </div>
      <div class="form-group">
        <label for="latitudeInput">Latitude:</label>
        <input type="text" id="latitudeInput" v-model="latitude" placeholder="Enter latitude">
      </div>
      <div class="form-group">
        <label for="longitudeInput">Longitude:</label>
        <input type="text" id="longitudeInput" v-model="longitude" placeholder="Enter longitude">
      </div>
      <button type="submit">Get Availability</button>
    </form>
    <!-- Display the result -->
    <pre v-if="itemResult">{{ itemResult }}</pre>
  </div>
</template>

<script>
export default {
  name: 'HomeComponent',
  props: {
    msg: String
  },
  data() {
    return {
      datetime: '',
      latitude: '',
      longitude: '',
      itemResult: null // This will hold the result from the API call
    };
  },
  methods: {
    async getItem() {
      try {
        // Fetching the parking availability data
        const response = await fetch(`/api/v1/items/datetime/${this.datetime}/latitude/${this.latitude}/longitude/${this.longitude}`);
        if (!response.ok) {
          this.itemResult = 'No response was obtained';
          return;
        }
        const data = await response.json();
        this.itemResult = `For the datetime ${this.datetime} and location lat: ${this.latitude} and long: ${this.longitude}, the parking availability is: ${data.result}`;
      } catch (error) {
        console.error('Error fetching availability:', error);
        this.itemResult = 'Error fetching availability';
      }
    }
  }
}
</script>

<!-- Styles for your component -->
<style scoped>
.availability-form {
  max-width: 300px;
  margin: auto;
}

.availability-form .form-group {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.availability-form .form-group label {
  flex-basis: 30%;
  margin-right: 1px;
}

.availability-form .form-group input {
  flex: 1;
}

button {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  background-color: #42b983;
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

button:hover {
  background-color: #367d62;
}
</style>
