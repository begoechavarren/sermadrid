<template>
  <div class="home">
    <Home />
  </div>
</template>

<script>
import Home from '@/components/Home.vue';

export default {
  name: 'HomeView',
  components: {
    Home
  }
}
</script>

<style scoped>
.home {
  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100vw;
}
</style>
