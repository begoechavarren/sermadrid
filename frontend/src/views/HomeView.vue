<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png" style="width: 150px; height: 150px;">
    <Home msg="sermadrid"/>
  </div>
</template>

<script>
// @ is an alias to /src
import Home from '@/components/Home.vue'

export default {
  name: 'HomeView',
  components: {
    Home
  }
}
</script>
