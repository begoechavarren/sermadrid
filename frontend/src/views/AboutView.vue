<template>
  <div class="about">
    <p>
      👩‍💻 Built by <a href="https://github.com/begoechavarren" target="_blank" rel="noopener">@begoechavarren</a><br>
      at <a href="https://github.com/begoechavarren/sermadrid" target="_blank" rel="noopener">
        <font-awesome-icon :icon="['fab', 'github']" /> sermadrid
      </a>
    </p>
    <div class="home-icon" @click="goToHome">
      <font-awesome-icon :icon="['fas', 'home']" />
    </div>
  </div>
</template>

<script>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { faHome } from '@fortawesome/free-solid-svg-icons'

library.add(faGithub, faHome)

export default {
  name: 'AboutView',
  components: {
    FontAwesomeIcon
  },
  methods: {
    goToHome() {
      this.$router.push({ name: 'home' });
    }
  }
}
</script>

<style scoped>
.about {
  text-align: center;
  margin-top: 50px;
}

.about p {
  font-size: 1.5em;
}

.about a {
  color: #42b983;
}

.home-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 2;
  font-size: 24px;
  cursor: pointer;
  color: #42b983;
}
</style>
