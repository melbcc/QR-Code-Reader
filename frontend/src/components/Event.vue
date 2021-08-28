<template>
  <div class="event">
    <i v-if="selected" class="fas fa-check-circle"></i>
    <i v-else class="far fa-circle"></i>
    {{ title }}
  </div>
</template>

<script>
  export default {
    props: {
      title: String,
      selected: Boolean,
    },
  }
</script>

<style scoped>
  .event {
    display: block;
    border-radius: 30px;
    background-color: lightsteelblue;
    margin: 0.2em;
    padding: 0.5em 1em;
    font-size: 1.5em;
  }
</style>
