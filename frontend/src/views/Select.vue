<template>
    <div v-swipe:left="navNext" class="view">
        <Spinner loadkey="events" v-on:click="fetchEvents" />
        <h1>Select Event</h1>
        <Event
            v-for="event in events"
            :pk="event.pk"
            :title="event.title"
            :key="event.pk"
        />
        <div id="begin-button" v-on:click="navNext">
            Begin: <i class="fas fa-qrcode" />&nbsp;<i class="fas fa-chevron-right" />&nbsp;<i class="fas fa-camera" />
        </div>
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
    #begin-button {
        color: white;
        background-color: dodgerblue;
        border-radius: 3vh;
        padding: 2vh 5vw;
        text-align: center;
        font-size: 4vw;
        width: 50vw;
        margin: 5vh 25vw;
    }
</style>
