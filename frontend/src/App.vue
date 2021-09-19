<template>
    <div>
        <NavBar />
        <div id="app-view">
            <router-view />
        </div>
    </div>
</template>

<script>
    //import HelloWorld from './components/HelloWorld.vue'
    import NavBar from './components/NavBar.vue'

    export default {
        name: 'App',
        components: {
            NavBar,
        },
        created() {
            this.$store.getters.csrftoken  // getter fetches value
            this.$store.dispatch('fetchEvents')  // prevents empty events on reload
        },
    }
</script>

<style>
    #app {
        font-family: Avenir, Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        color: #2c3e50;
    }

    #app-view {
        padding: 10vh 0 5vh;
    }

    h1 {
        margin: 0 5vw;
    }
</style>
