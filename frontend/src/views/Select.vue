<template>
  <div v-swipe:left="navNext">
    <h1>Select Event</h1>
    <h2>Events</h2>
    <Event
      v-for="event in events"
      v-bind:key="event.index"
      v-bind:title="event.title"
      v-bind:selected="event.selected"
    />
    <h2>Filter</h2>
    <router-link to="/scan">
      Begin Scanning <i class="fas fa-camera" /> &gt;&gt;
    </router-link>
  </div>
</template>

<script>
  import Event from '../components/Event.vue'
  export default {
    components: {
      Event,
    },
    data() {
      return {
        events: [
          {
            index: 0,
            title: "Northern Suburbs Linux SIG",
            selected: true,
          },
          {
            index: 1,
            title: "Website Design SIG",
            selected: true,
          },
          {
            index: 2,
            title: "Coder Dojo 2021",
            selected: false,
          },
        ],
      }
    },
    methods: {
      navNext() { this.$router.push('/scan') },
    },
  }
</script>

<style scoped>
</style>
