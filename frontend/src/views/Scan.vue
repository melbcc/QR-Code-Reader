<template>
  <div v-swipe:left="navNext" v-swipe:right="navPrev">
    <h1>Scan Attendees</h1>
  </div>
</template>

<script>
  export default {
    methods: {
      navPrev() { this.$router.push('/select') },
      navNext() { this.$router.push('/list') },
    },
  }
</script>

<style scoped>
</style>
