<template>
  <div v-swipe:left="navNext">
    <h1>Select Event</h1>
  </div>
</template>

<script>
  export default {
    methods: {
      navNext() { this.$router.push('/scan') },
    },
  }
</script>

<style scoped>
</style>
