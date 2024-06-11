<template>
  <div class="home">
    <div id="map" class="map-container"></div>
    <div class="header">
      <img alt="sermadrid logo" src="../assets/logo.png" class="logo">
      <div class="header-text">
        <h1>sermadrid</h1>
        <p>Select the location and time where you would like to park in the Madrid SER zone</p>
      </div>
    </div>
    <form @submit.prevent="getItem" class="availability-form">
      <div class="form-group">
        <flat-pickr v-model="datetime" :config="config" class="form-control" placeholder="Select date and time"></flat-pickr>
      </div>
      <button type="submit" class="availability-button">Get Availability</button>
    </form>
    <div v-if="itemResult" class="result-output">
      {{ itemResult }}
    </div>
    <div class="about-icon" @click="goToAbout">
      <font-awesome-icon :icon="['fas', 'info-circle']" />
    </div>
  </div>
</template>

<script>
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import FlatPickr from "vue-flatpickr-component";
import "flatpickr/dist/flatpickr.css";
import * as turf from "@turf/turf";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import limiteZonaSer from "../assets/ser_zone_limit.geojson";
import neighbourhoodLimits from "../assets/neighbourhood_limits.geojson";

export default {
  name: "HomeComponent",
  components: {
    FlatPickr,
    FontAwesomeIcon,
  },
  data() {
    const currentDate = new Date();
    const formattedDate =
      currentDate.getFullYear() +
      "-" +
      ("0" + (currentDate.getMonth() + 1)).slice(-2) +
      "-" +
      ("0" + currentDate.getDate()).slice(-2) +
      " " +
      ("0" + currentDate.getHours()).slice(-2) +
      ":" +
      ("0" + currentDate.getMinutes()).slice(-2) +
      ":00"; // Set seconds to 00
    return {
      datetime: formattedDate,
      itemResult: null,
      map: null,
      marker: null,
      latitude: null,
      longitude: null,
      neighbourhood_id: null,
      clickedFeature: null,
      showOutsideMessage: false,
      messagePosition: { x: 0, y: 0 },
      config: {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        defaultDate: new Date(),
        minDate: "today",
        time_24hr: true,
      },
    };
  },
  mounted() {
    mapboxgl.accessToken = process.env.VUE_APP_MAPBOX_TOKEN;
    this.map = new mapboxgl.Map({
      container: "map",
      style: "mapbox://styles/mapbox/streets-v11",
      center: [-3.694241, 40.4167754],
      zoom: 12,
      minZoom: 10.5,
      maxBounds: [
        [-4.1, 40.37], // Southwest
        [-3.3, 40.5], // Northeast
      ],
    });

    const updateMask = () => {
      const bounds = this.map.getBounds().toArray().flat();
      const expandedBounds = [
        bounds[0] - 1, // west (left) bound - expand by 1 degree
        bounds[1] - 1, // south (bottom) bound - expand by 1 degree
        bounds[2] + 1, // east (right) bound - expand by 1 degree
        bounds[3] + 1, // north (top) bound - expand by 1 degree
      ];
      const bboxPoly = turf.bboxPolygon(expandedBounds);
      const maskGeometry = limiteZonaSer.features[0].geometry;
      let firstPolygonGeometry;

      if (maskGeometry.type === "MultiPolygon") {
        firstPolygonGeometry = {
          type: "Polygon",
          coordinates: maskGeometry.coordinates[0],
        };
      } else {
        firstPolygonGeometry = maskGeometry;
      }

      const mask = turf.difference(bboxPoly, firstPolygonGeometry);

      if (!mask) {
        console.error("Unable to create mask from the given MultiPolygon.");
        return;
      }

      if (this.map.getSource("mask")) {
        this.map.getSource("mask").setData(mask);
      } else {
        this.map.addSource("mask", {
          type: "geojson",
          data: mask,
        });

        this.map.addLayer({
          id: "mask",
          source: "mask",
          type: "fill",
          paint: {
            "fill-color": "#000",
            "fill-opacity": 0.2,
          },
        });
      }
    };

    this.map.on("load", () => {
      updateMask();

      // Add neighborhood limits as a new source without showing the lines initially
      this.map.addSource("neighbourhoodLimits", {
        type: "geojson",
        data: neighbourhoodLimits,
      });
    });

    this.map.on("moveend", updateMask);

    this.map.on("click", this.mapClickHandler);
  },
  methods: {
    mapClickHandler(e) {
      const point = turf.point([e.lngLat.lng, e.lngLat.lat]);
      const within = turf.booleanPointInPolygon(
        point,
        limiteZonaSer.features[0].geometry
      );
      if (within) {
        this.latitude = e.lngLat.lat;
        this.longitude = e.lngLat.lng;
        if (this.marker) {
          this.marker.remove();
        }
        this.marker = new mapboxgl.Marker()
          .setLngLat([this.longitude, this.latitude])
          .addTo(this.map);

        // Find the neighborhood the point is in
        this.clickedFeature = null;
        for (const feature of neighbourhoodLimits.features) {
          if (turf.booleanPointInPolygon(point, feature)) {
            const properties = feature.properties;
            this.neighbourhood_id = this.formatNeighbourhoodId(properties.CODDIS, properties.CODBAR);
            this.clickedFeature = feature;
            break;
          }
        }

      } else {
        // Show the message and update the position
        this.messagePosition = {
          x: e.originalEvent.clientX,
          y: e.originalEvent.clientY,
        };
        this.showOutsideMessage = true;
        // Use a timeout to hide the message after 2 seconds
        clearTimeout(this.hideMessageTimeout);
        this.hideMessageTimeout = setTimeout(() => {
          this.showOutsideMessage = false;
        }, 2000);
      }
    },
    formatNeighbourhoodId(CODDIS, CODBAR) {
      // Ensure CODBAR is always two digits
      const formattedCODBAR = String(CODBAR).padStart(2, '0');
      return `${CODDIS}${formattedCODBAR}`;
    },
    capitalizeWords(str) {
      return str
        .toLowerCase()
        .replace(/\b\w/g, function (l) { return l.toUpperCase(); });
    },
    async getItem() {
      // Check if neighbourhood_id is set
      if (this.neighbourhood_id === null) {
        this.itemResult = "Please select the location in the Madrid SER zone map";
        return; // Exit the function early
      }

      try {
        const response = await fetch(
          `/api/v1/items/datetime/${this.datetime}/neighbourhood_id/${this.neighbourhood_id}`
        );
        if (!response.ok) {
          throw new Error("Network response was not ok.");
        }
        const data = await response.json();
        const taskId = data.task_id;

        // Polling for the task result
        let result;
        while (!result) {
          const resultResponse = await fetch(`/api/v1/items/result/${taskId}`);
          if (resultResponse.status === 202) {
            // Task is still pending
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second before polling again
          } else if (resultResponse.status === 200) {
            // Task completed successfully
            result = await resultResponse.json();
          } else {
            // Task failed
            throw new Error("Task failed");
          }
        }

        // Highlight the selected neighborhood when the result is shown
        if (this.clickedFeature) {
          const highlightSourceId = 'highlight';
          if (this.map.getSource(highlightSourceId)) {
            this.map.getSource(highlightSourceId).setData(this.clickedFeature);
          } else {
            this.map.addSource(highlightSourceId, {
              type: 'geojson',
              data: this.clickedFeature,
            });
            this.map.addLayer({
              id: 'highlight',
              type: 'fill',
              source: highlightSourceId,
              paint: {
                'fill-color': '#90ee90', // light green color similar to the availability button but lighter and transparent
                'fill-opacity': 0.5,
              },
            });
          }
        }

        this.itemResult = `For the datetime ${this.datetime} and neighbourhood ${this.capitalizeWords(result.barrio)}, the percentage of available parking spots is ${parseInt(result.prediction * 100)}% (${result.result})`;
      } catch (error) {
        this.itemResult = "Error fetching availability: " + error.message;
      }
    },
    goToAbout() {
      this.$router.push({ name: 'about' });
    },
  },
  computed: {
    messageStyle() {
      return {
        top: this.messagePosition.y + "px",
        left: this.messagePosition.x + "px",
      };
    },
  },
};
</script>

<style scoped>
.home {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  margin: 0; /* Remove any default margin */
  padding: 0; /* Remove any default padding */
}

.map-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.header {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 2;
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 10px;
  border-radius: 10px;
}

.logo {
  width: 60px;
  height: 60px;
  margin-right: 10px;
}

.header-text h1, .header-text p {
  margin: 0;
}

.availability-form {
  position: absolute;
  top: 120px;
  left: 20px;
  z-index: 2;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 10px;
  border-radius: 10px;
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
  background-color: #42b983;
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.result-output {
  position: absolute;
  bottom: 70px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  font-weight: bold;
  text-align: center;
  margin-top: 20px;
  font-size: 1em;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 10px;
  border-radius: 10px;
}

.outside-message {
  position: fixed;
  background: white;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
  pointer-events: none;
  transform: translate(-50%, -50%);
  z-index: 1000; /* Ensure it's above map elements */
}

.about-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 2;
  font-size: 24px;
  cursor: pointer;
  color: #42b983;
}
</style>
