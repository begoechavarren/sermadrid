<template>
  <div class="home">
    <h1>{{ msg }}</h1>
    <p>Select the location and time where you would like to park in the Madrid SER zone</p>
    <div id="map" class="map-container"></div>
    <form @submit.prevent="getItem" class="availability-form">
      <div class="form-group">
        <label for="datetimeInput">Datetime:</label>
        <input type="text" id="datetimeInput" v-model="datetime" placeholder="Enter datetime">
      </div>
      <button type="submit" class="availability-button">Get Availability</button>
    </form>
    <pre v-if="itemResult">{{ itemResult }}</pre>
  </div>
</template>

<script>
import mapboxgl from 'mapbox-gl';

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
      itemResult: null,
      map: null,
      marker: null
    };
  },
  mounted() {
    mapboxgl.accessToken = process.env.VUE_APP_MAPBOX_TOKEN;
    this.map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [-3.7037902, 40.4167754],
      zoom: 12
    });

    this.map.addControl(new mapboxgl.NavigationControl());

    this.map.on('load', () => {
      this.marker = new mapboxgl.Marker();
      this.map.on('click', (e) => {
        this.latitude = e.lngLat.lat;
        this.longitude = e.lngLat.lng;
        if (this.marker) {
          this.marker.remove(); // Remove the previous marker if there is one
        }
        this.marker = new mapboxgl.Marker()
          .setLngLat([this.longitude, this.latitude])
          .addTo(this.map);
      });
    });
  },
  methods: {
    async getItem() {
      try {
        const response = await fetch(`/api/v1/items/datetime/${this.datetime}/latitude/${this.latitude}/longitude/${this.longitude}`);
        if (!response.ok) {
          throw new Error('Network response was not ok.');
        }
        const data = await response.json();
        this.itemResult = `For the datetime ${this.datetime} and location lat: ${this.latitude}, long: ${this.longitude}, the parking availability is: ${data.result}`;
      } catch (error) {
        this.itemResult = 'Error fetching availability: ' + error.message;
      }
    }
  }
};
</script>

<style scoped>
.map-container {
  height: 300px;
  margin-bottom: 20px;
}

.availability-form {
  max-width: 300px;
  margin: auto;
}

.availability-form .form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.availability-form .form-group label {
  margin-bottom: 5px;
}

.availability-form .form-group input {
  flex: 1;
  padding: 8px;
}

.availability-button {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  background-color: #42b983;
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.availability-button:hover {
  background-color: #367d62;
}
</style>
