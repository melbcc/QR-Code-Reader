<template>
    <div v-swipe:right="navPrev" class="view">
        <Spinner loadkey="attendees" v-on:click="fetchEvents" />
        <h1>List of Attendees</h1>
        <div v-for="event in events"
             :key="event.pk"
             class="event"
        >
            <h2>{{ event.title }}</h2>
            <ul class="attendees">
                <li v-for="attendee in event.attendees"
                    :key="attendee.pk"
                >
                    <Attendee :obj="attendee" />
                </li>
                <li v-if="!event.attendees.length">(empty)</li>
            </ul>
        </div>
        <div v-if="!activeEvents?.length" class="message">
            <i class="fas fa-info-circle"/> There are no active events at this time.
        </div>
        <div v-else-if="!events.length" class="message">
            <i class="fas fa-info-circle"/> Please <router-link to="select">select an event</router-link> first.
        </div>
    </div>
</template>

<script>
    import axios from 'axios'

    import Attendee from '../components/Attendee.vue'
    import Spinner from '../components/Spinner.vue'

    export default {
        components: {
            Attendee,
            Spinner,
        },
        data() {
            return {
                events: [], // list of responses from /api/eventdetail/:pk/
            }
        },
        computed: {
            activeEvents() {
                return this.$store.state.events.active
            },
        },
        methods: {
            // Navigation
            navPrev() { this.$router.push({name: 'Scan'}) },
            fetchEvents() {
                const settings = this.$store.state.settings
                const eventStack = ( // which events to fetch
                    settings.listAttendanceFromAll ?
                    this.$store.state.events.active :
                    this.$store.getters.selectedEvents
                )
                this.$store.commit('SET_LOADING', {key: 'attendees', isLoading: true})
                axios.all(eventStack.map(
                    // multiple requests, processed in parallel
                    (event) => axios.get(`/api/eventdetail/${event.pk}/`)
                )).then(
                    (responses) => { // success
                        this.$store.commit('SET_LOADING', {key: 'attendees', isLoading: false})
                        this.events = responses.map((response) => response.data)
                    }
                ).catch(
                    (errors) => { // failure
                        this.$store.commit('SET_LOADING', {key: 'attendees', isLoading: false})
                        this.$store.commit('SET_ERROR', {title: "Error fetching attendance", message: errors})
                    }
                )
            },
        },
        mounted() {
            this.$store.dispatch('fetchEvents')
            this.fetchEvents()
        },
    }
</script>

<style lang="scss" scoped>
    .event {
        margin: 2vw 2vh;
        border-width: 2px;
        border: grey;
        border-radius: 2em;
        //background-color: lightgrey;
        border-style: solid;
        h2 {
            font-weight: bold;
            font-size: 3vh;
            margin: 2vw 2vh;
        }
        ul {
            list-style-type: none;
        }
    }
    .message {
        font-size: 2em;
        text-align: center;
        padding: 2em;
    }
</style>
