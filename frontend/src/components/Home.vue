<template>
  <div class="home">
    <h1>sermadrid</h1>
    <p>
      Select the location and time where you would like to park in the Madrid
      SER zone
    </p>
    <div id="map" class="map-container"></div>
    <div
      v-show="showOutsideMessage"
      class="outside-message"
      :style="messageStyle"
    >
      Out of the SER zone
    </div>
    <form @submit.prevent="getItem" class="availability-form">
      <div class="form-group">
        <flat-pickr
          v-model="datetime"
          :config="config"
          class="form-control"
          placeholder="Select date and time"
        ></flat-pickr>
      </div>
      <button type="submit" class="availability-button">
        Get Availability
      </button>
    </form>
    <div v-if="itemResult" class="result-output">
      {{ itemResult }}
    </div>
  </div>
</template>

<script>
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import FlatPickr from "vue-flatpickr-component";
import "flatpickr/dist/flatpickr.css";
import * as turf from "@turf/turf";
import limiteZonaSer from "../assets/ser_zone_limit.geojson";

export default {
  name: "HomeComponent",
  components: {
    FlatPickr,
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

    this.map.on("load", updateMask);
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
    createMask(maskFeatureCollection, bounds) {
      var bboxPoly = turf.bboxPolygon(bounds);
      var maskGeometry = maskFeatureCollection.features[0].geometry;

      // Check if the geometry is a MultiPolygon and use the first Polygon
      if (maskGeometry.type === "MultiPolygon") {
        // Extract the first polygon's coordinates from the MultiPolygon
        var firstPolygonCoordinates = maskGeometry.coordinates[0];
        // Create a Polygon geometry from the first set of coordinates
        maskGeometry = {
          type: "Polygon",
          coordinates: firstPolygonCoordinates,
        };
      }

      // Perform the difference operation
      var masked = turf.difference(bboxPoly, maskGeometry);

      // Check if the operation was successful
      if (!masked) {
        throw new Error(
          "Difference operation failed. The mask might not be subtracting correctly."
        );
      }

      return masked;
    },
    async getItem() {
      // Check if latitude and longitude are set
      if (this.latitude === null || this.longitude === null) {
        this.itemResult = "Please select the location in the Madrid SER zone map";
        return; // Exit the function early
      }

      try {
        const response = await fetch(
          `/api/v1/items/datetime/${this.datetime}/latitude/${this.latitude}/longitude/${this.longitude}`
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

        this.itemResult = `For the datetime ${this.datetime} and location lat: ${this.latitude}, long: ${this.longitude}, the parking availability is: ${result.result}`;
      } catch (error) {
        this.itemResult = "Error fetching availability: " + error.message;
      }
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

.availability-button:hover {
  background-color: #367d62;
}

.result-output {
  font-weight: bold;
  text-align: center;
  margin-top: 20px;
  font-size: 1em;
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
</style>
