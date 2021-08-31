<template>
    <div v-swipe:left="navNext">
        <h1>Select Event</h1>
        <Spinner loadkey="events" v-on:click="fetchEvents" />
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
    import Spinner from '../components/Spinner.vue'

    export default {
        components: {
            Spinner,
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
            eventsSpinnerClass() {
                return this.$store.state.loading.events ? 'rotating' : '';
            },
        },
        methods: {
            navNext() { this.$router.push('/scan') },
            fetchEvents() {
                this.$store.dispatch('fetchEvents');
            },
        },
        mounted() {
            this.fetchEvents()
        },
    }
</script>

<style scoped>
</style>
