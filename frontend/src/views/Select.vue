<template>
  <div v-swipe:left="navNext">
    <h1>Select Event</h1>
    <h2>Events</h2>
    <Event
      v-for="event in events"
      :pk="event.pk"
      :title="event.title"
      :key="event.pk"
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
        // TODO: needed?
      }
    },
    computed: {
      events() {
        return this.$store.state.events.active;
      },
    },
    methods: {
      navNext() { this.$router.push('/scan') },
    },
    mounted() {
      this.$store.dispatch('fetchEvents');
    },
  }
</script>

<style scoped>
</style>
