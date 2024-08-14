<template>
  <div class="home">
    <div id="map" class="map-container"></div>
    <div class="header">
      <img alt="sermadrid logo" src="../assets/logo.png" class="logo">
      <div class="header-text">
        <h1>sermadrid</h1>
      </div>
    </div>
    <form @submit.prevent="getItem" class="availability-form">
      <p class="form-description">
        Select the location and time where you would like to park in the <br>
        Madrid SER zone
      </p>
      <div class="form-group">
        <input
          v-model="address"
          type="text"
          class="form-control"
          placeholder="Enter address or click on the map"
          @input="getSuggestions"
        />
        <ul v-if="suggestions.length" class="suggestions-list">
          <li
            v-for="(suggestion, index) in suggestions"
            :key="index"
            @click="selectSuggestion(suggestion)"
          >
            {{ suggestion.place_name }}
          </li>
        </ul>
      </div>
      <div class="form-group">
        <flat-pickr
          v-model="datetime"
          :config="config"
          class="form-control"
          placeholder="Select date and time"
        ></flat-pickr>
      </div>
      <button type="submit" class="availability-button">Get Availability</button>
    </form>
    <div v-if="itemResult" class="result-output">{{ itemResult }}</div>
    <div class="about-icon" @click="goToAbout">
      <font-awesome-icon :icon="['fas', 'info-circle']" />
    </div>
    <div v-if="showMessage" class="centered-message">
      {{ outsideMessage }}
    </div>
  </div>
</template>

<script>
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import FlatPickr from 'vue-flatpickr-component';
import 'flatpickr/dist/flatpickr.css';
import * as turf from '@turf/turf';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import limiteZonaSer from '../assets/ser_zone_limit.geojson';
import neighbourhoodLimits from '../assets/neighbourhood_limits.geojson';

export default {
  name: 'HomeComponent',
  components: {
    FlatPickr,
    FontAwesomeIcon,
  },
  data() {
    const currentDate = new Date();
    const formattedDate =
      currentDate.getFullYear() +
      '-' +
      ('0' + (currentDate.getMonth() + 1)).slice(-2) +
      '-' +
      ('0' + currentDate.getDate()).slice(-2) +
      ' ' +
      ('0' + currentDate.getHours()).slice(-2) +
      ':' +
      ('0' + currentDate.getMinutes()).slice(-2) +
      ':00';
    return {
      datetime: formattedDate,
      address: '',
      suggestions: [],
      itemResult: null,
      map: null,
      marker: null,
      latitude: null,
      longitude: null,
      neighbourhood_id: null,
      clickedFeature: null,
      showMessage: false,
      isAddressCheck: false,
      outsideMessage: '',
      messagePosition: { x: 0, y: 0 },
      config: {
        enableTime: true,
        dateFormat: 'Y-m-d H:i',
        defaultDate: new Date(),
        minDate: 'today',
        time_24hr: true,
      },
    };
  },
  mounted() {
    mapboxgl.accessToken = process.env.VUE_APP_MAPBOX_TOKEN;
    this.map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [-3.694241, 40.436185],
      zoom: 12,
      minZoom: 10.5,
      maxBounds: [
        [-4.1, 40.37],
        [-3.3, 40.5],
      ],
    });

    const updateMask = () => {
      const bounds = this.map.getBounds().toArray().flat();
      const expandedBounds = [
        bounds[0] - 1,
        bounds[1] - 1,
        bounds[2] + 1,
        bounds[3] + 1,
      ];
      const bboxPoly = turf.bboxPolygon(expandedBounds);
      const maskGeometry = limiteZonaSer.features[0].geometry;
      let firstPolygonGeometry;

      if (maskGeometry.type === 'MultiPolygon') {
        firstPolygonGeometry = {
          type: 'Polygon',
          coordinates: maskGeometry.coordinates[0],
        };
      } else {
        firstPolygonGeometry = maskGeometry;
      }

      const mask = turf.difference(bboxPoly, firstPolygonGeometry);

      if (!mask) {
        console.error('Unable to create mask from the given MultiPolygon.');
        return;
      }

      if (this.map.getSource('mask')) {
        this.map.getSource('mask').setData(mask);
      } else {
        this.map.addSource('mask', {
          type: 'geojson',
          data: mask,
        });

        this.map.addLayer({
          id: 'mask',
          source: 'mask',
          type: 'fill',
          paint: {
            'fill-color': '#000',
            'fill-opacity': 0.2,
          },
        });
      }
    };

    this.map.on('load', () => {
      updateMask();

      this.map.addSource('neighbourhoodLimits', {
        type: 'geojson',
        data: neighbourhoodLimits,
      });
    });

    this.map.on('moveend', updateMask);

    this.map.on('click', this.mapClickHandler);
  },
  methods: {
    async getSuggestions() {
      if (this.address.length < 3) {
        this.suggestions = [];
        return;
      }
      const response = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(this.address)}.json?access_token=${mapboxgl.accessToken}`
      );
      const data = await response.json();
      this.suggestions = data.features;
    },
    async selectSuggestion(suggestion) {
      this.address = suggestion.place_name;
      this.suggestions = [];
      const [lng, lat] = suggestion.center;
      this.handleCoordinates(lng, lat, true);
    },
    async geocodeAddress(address) {
      const response = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(address)}.json?access_token=${mapboxgl.accessToken}`
      );
      const data = await response.json();
      if (data.features && data.features.length > 0) {
        const [lng, lat] = data.features[0].center;
        return { lng, lat };
      } else {
        throw new Error('Address not found');
      }
    },
    async reverseGeocode(lng, lat) {
      const response = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?access_token=${mapboxgl.accessToken}`
      );
      const data = await response.json();
      if (data.features && data.features.length > 0) {
        return data.features[0].place_name;
      } else {
        throw new Error('Reverse geocoding failed');
      }
    },
    async mapClickHandler(e) {
      this.handleCoordinates(e.lngLat.lng, e.lngLat.lat, false, e.originalEvent);
    },
    async handleCoordinates(lng, lat, isAddress, event) {
      this.clearMessages();
      const point = turf.point([lng, lat]);
      const within = turf.booleanPointInPolygon(
        point,
        limiteZonaSer.features[0].geometry
      );
      if (within) {
        this.latitude = lat;
        this.longitude = lng;
        if (this.marker) {
          this.marker.remove();
        }
        this.marker = new mapboxgl.Marker()
          .setLngLat([this.longitude, this.latitude])
          .addTo(this.map);

        this.clearHighlight();

        this.clickedFeature = null;
        for (const feature of neighbourhoodLimits.features) {
          if (turf.booleanPointInPolygon(point, feature)) {
            const properties = feature.properties;
            this.neighbourhood_id = this.formatNeighbourhoodId(properties.CODDIS, properties.CODBAR);
            this.clickedFeature = feature;
            break;
          }
        }

        if (!isAddress) {
          const placeName = await this.reverseGeocode(lng, lat);
          this.address = placeName;
        }

        this.showMessage = false;
        this.itemResult = null;
      } else {
        this.clearMessages();
        this.showMessage = true;
        this.outsideMessage = 'Please select an address within the Madrid SER zone';
        this.clearMarker();
        this.clearHighlight();
        this.address = '';
        this.itemResult = null;

        const viewportWidth = window.innerWidth;
        const messageBoxWidth = 160;
        const x = event.clientX;
        let y = event.clientY;

        if (x <= viewportWidth / 2) {
          this.messagePosition = { x: Math.min(x + messageBoxWidth, viewportWidth - messageBoxWidth), y };
        } else {
          this.messagePosition = { x: Math.max(x - messageBoxWidth, 0), y };
        }

        this.isAddressCheck = !event;
        this.neighbourhood_id = null;
      }
    },
    clearMessages() {
      this.showMessage = false;
      this.itemResult = null;
      this.clearHighlight();
    },
    clearMarker() {
      if (this.marker) {
        this.marker.remove();
      }
      this.marker = null;
    },
    clearHighlight() {
      if (this.map.getLayer('highlight')) {
        this.map.removeLayer('highlight');
      }
      if (this.map.getSource('highlight')) {
        this.map.removeSource('highlight');
      }
      this.clickedFeature = null;
    },
    formatNeighbourhoodId(CODDIS, CODBAR) {
      const formattedCODBAR = String(CODBAR).padStart(2, '0');
      return `${CODDIS}${formattedCODBAR}`;
    },
    capitalizeWords(str) {
      return str
        .toLowerCase()
        .replace(/\b\w/g, function (l) {
          return l.toUpperCase();
        });
    },
    getColorForAvailability(prediction) {
      if (prediction <= 0.2) {
        return '#FF0000';
      } else if (prediction <= 0.4) {
        return '#FFA500';
      } else {
        return '#90EE90';
      }
    },
    async getItem() {
      this.clearMessages();
      if (!this.address) {
        this.showMessage = true;
        this.outsideMessage = 'Please select the address where you would like to park';
        this.isAddressCheck = true;
        return;
      }
      if (this.neighbourhood_id === null) {
        this.showMessage = true;
        this.outsideMessage = 'Please select an address within the Madrid SER zone';
        this.isAddressCheck = true;
        return;
      }

      const date = new Date(this.datetime);
      const day = date.getDay();
      const hour = date.getHours();

      const month = date.getMonth(); // 7 = August

    if (
        (month === 7 && day >= 1 && day <= 5 && hour >= 15) ||
        day === 0 || 
        (day >= 1 && day <= 5 && (hour < 9 || hour >= 21)) ||
        (day === 6 && hour >= 15) ||
        (day === 7)
    ) {
      this.clearMessages();
      this.showMessage = true;
      this.outsideMessage = 'Please select a time within the Madrid SER zone schedule';
      this.clearHighlight();
      return;
    }

      try {
        if (this.address) {
          const coords = await this.geocodeAddress(this.address);
          await this.handleCoordinates(coords.lng, coords.lat, true);
        }
        if (this.neighbourhood_id === null) {
          this.itemResult = 'Please select an address within the Madrid SER zone';
          this.showMessage = true;
          this.outsideMessage = 'Please select an address within the Madrid SER zone';
          this.isAddressCheck = true;
          return;
        }

        const response = await fetch(
          `/api/v1/items/datetime/${this.datetime}/neighbourhood_id/${this.neighbourhood_id}`
        );
        if (!response.ok) {
          throw new Error('Network response was not ok.');
        }
        const result = await response.json();

        if (this.clickedFeature) {
          const highlightSourceId = 'highlight';
          const fillColor = this.getColorForAvailability(result.prediction);
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
                'fill-color': fillColor,
                'fill-opacity': 0.5,
              },
            });
          }
          this.map.setPaintProperty('highlight', 'fill-color', fillColor);
        }

        this.itemResult = `For the datetime ${this.datetime} and neighbourhood ${this.capitalizeWords(
          result.barrio
        )}, the percentage of available parking spots is ${parseInt(result.prediction * 100)}%`;
      } catch (error) {
        this.itemResult = 'Error fetching availability: ' + error.message;
      }
    },
    goToAbout() {
      this.$router.push({ name: 'about' });
    },
  },
  computed: {
    messageStyle() {
      return this.isAddressCheck
        ? {}
        : {
            top: `${this.messagePosition.y}px`,
            left: `${this.messagePosition.x}px`,
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
  margin: 0;
  padding: 0;
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
  padding: 2px 2px;
  border-radius: 10px;
  width: 280px;
  height: 120px;
}

.logo {
  width: 107.52px;
  height: 107.52px;
}

.header-text {
  margin-left: -20px;
}

.header-text h1 {
  margin: 0;
  font-size: 1.82em;
  margin-right: 20px;
}

.availability-form {
  position: absolute;
  top: 150px;
  left: 20px;
  z-index: 2;
  width: 280px;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 10px;
  border-radius: 10px;
}

.form-description {
  margin: 0 0 10px 0;
  white-space: normal;
  max-width: 100%;
  line-height: 1.5em;
}

.availability-form .form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 5px;
  position: relative;
}

.availability-form .form-control {
  padding: 8px;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
  background: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  position: absolute;
  top: 38px;
  width: 100%;
  z-index: 3;
}

.suggestions-list li {
  padding: 8px;
  cursor: pointer;
}

.suggestions-list li:hover {
  background: #f0f0f0;
}

.availability-button {
  width: 100%;
  padding: 8px;
  background-color: #42b983;
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 5px;
  margin-top: 5px;
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

.outside-message,
.centered-message {
  position: absolute;
  background: rgba(255, 255, 255, 0.8);
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 10px;
  pointer-events: none;
  z-index: 1000;
  text-align: center;
  font-weight: bold;
  width: 300px;
}

.outside-message {
  transform: translate(-50%, -50%);
}

.centered-message {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
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
