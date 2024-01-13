<template>
  <div class="home">
    <h1>sermadrid</h1>
    <p>Select the location and time where you would like to park in the Madrid SER zone</p>
    <div id="map" class="map-container"></div>
    <form @submit.prevent="getItem" class="availability-form">
      <div class="form-group">
        <flat-pickr v-model="datetime" :config="config" class="form-control" placeholder="Select date and time"></flat-pickr>
      </div>
      <button type="submit" class="availability-button">Get Availability</button>
    </form>
    <pre v-if="itemResult">{{ itemResult }}</pre>
  </div>
</template>

<script>
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import FlatPickr from 'vue-flatpickr-component';
import 'flatpickr/dist/flatpickr.css';

export default {
  name: 'HomeComponent',
  components: {
    FlatPickr
  },
  data() {
    return {
      datetime: '',
      itemResult: null,
      map: null,
      marker: null,
      config: {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        defaultDate: new Date(),
        minDate: "today",
        time_24hr: true
      }
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
  flex-direction: column
}

.availability-form .form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.availability-form .form-group label {
  margin-bottom: 5px;
}

.availability-form .form-control {
  padding: 8px;
  margin-bottom: 10px;
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

