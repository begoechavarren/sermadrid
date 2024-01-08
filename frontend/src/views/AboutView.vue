<template>
  <div class="about">
      <p>
        👩‍💻 Built by <a href="https://github.com/begoechavarren" target="_blank" rel="noopener">@begoechavarren</a><br>
        at <a href="https://github.com/begoechavarren/sermadrid" target="_blank" rel="noopener">
          <font-awesome-icon :icon="['fab', 'github']" /> sermadrid
        </a>
      </p>
  </div>
</template>


<script>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faGithub } from '@fortawesome/free-brands-svg-icons'

library.add(faGithub)

export default {
  name: 'AboutView',
  components: {
    FontAwesomeIcon
  }
}
</script>


<style scoped>
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
