<template>
  <div class="nav-bar">
    <span v-for="(route, i) in navRoutes" :key="i" class="nav-bar-item">
      <router-link :to="route.path" exact-active-class="active">
        <i :class="route.meta.icon" /> {{ route.name }}
      </router-link>
    </span>
  </div>
</template>

<script>
  export default {
    name: 'NavBar',
    computed: {
      navRoutes() {
        return this.$router.options.routes.filter(r => r?.meta?.nav === true)
      },
    },
  }
</script>

<style scoped>
  .nav-bar {
    position: fixed;
    top: 0;
    display: block;
    width: 100vw;
    height: 13vw;
    background: black;
  }
  .nav-bar-item a {
    display: inline-block;
    color: white;
    text-align: center;
    padding: 3vw;
    width: 28vw;
    text-decoration: none;
    font-size: 4vw;
    border-radius: 2vw;
  }
  .nav-bar-item .active {
    background-color: dodgerblue;
    color: white;
  }
</style>
