<template>
    <div class="nav-bar">
        <!-- Burger Menu Toggle button -->
        <input type="checkbox" class="burger-checkbox" id="burger-checkbox" v-on:click="burgerClick" />
        <label for="burger-checkbox" class="burger-button">
            <i class="fas fa-cog" id="burger-icon" />
        </label>
        <div class="burger-menu">
            <h2>Options</h2> <!-- TODO: make interactive -->
            <ul>
                <li><span>Logout</span></li>
                <li><span>Kiosk mode <i class="fas fa-info-circle"/></span></li>
                <li><span>Camera: overlay <i class="fas fa-info-circle"/></span></li>
                <li><span>Duplicate delay <i class="fas fa-info-circle"/></span></li>
                <li><span>Confirmation delay <i class="fas fa-info-circle"/></span></li>
                <li><span>Sounds on/off</span></li>
                <li><span>List attendees from all events</span></li>
                <li><span>Keep camera on <i class="fas fa-info-circle"/></span></li>
            </ul>
        </div>
        <!-- Navigation Buttons -->
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
                return this.$router.options.routes
                .filter(r => r?.meta?.nav === true)
            },
        },
        methods: {
            burgerClick(event) {
                // Treat burger as modal, to disable camera rendering (which is always on top)
                this.$store.dispatch('modalDisplayOpen', event.target.checked ? 'burger-menu' : null);
            },
        },
    }
</script>

<style>
    /* ----- Burger Menu ----- */
    #burger-checkbox {
        display: none;
    }

    .burger-button {
        position: absolute;
        top: 1vh;
        right: 1vh;
        width: 6vh;
        height: 6vh;
        border-radius: 50%;
        background-color: black;
        z-index: 1000;
        text-align: center;
        vertical-align: middle;
        cursor: pointer;
        transition: all 0.75s;
    }

    #burger-icon {
        font-size: 4vh;
        color: dodgerblue;
        height: 100%;
    }

    .burger-menu {
        position: absolute;
        z-index: 999;

        top: 0vh;
        right: 0vw;
        height: 100vh;
        width: 75vw;

        border-top-left-radius: 5vh;
        border-bottom-left-radius: 5vh;

        transition: all 0.5s;
        transform: translateX(75vw);
        
        padding: 4vh 5vw 20vh 8vw;
        font-size: 5vw;
        
        overflow: auto;
    }

    #burger-checkbox:checked ~ .burger-menu {
        display: block;
        background: lightsteelblue;

        transform: translateX(0vw);
        box-shadow: 0 0 3vw 2vw rgba(0, 0, 0, 0.3);
    }
    #burger-checkbox:checked ~ .burger-button {
        transform: rotate(180deg);
        box-shadow: 0 0 2vw 1vw rgba(0, 0, 0, 0.2);
    }
    
    /* FIXME: camera stream overlaps menu
    .qrcode-stream-wrapper ~ #burger-checkbox:checked {
        display: none;
    }
    */

    /* ----- Navigation Bar ----- */
    .nav-bar {
        position: fixed;
        top: 0;
        display: block;
        width: 100vw;
        height: 8vh;
        background: black;
    }

    .nav-bar-item a {
        display: table-cell;
        color: dodgerblue;
        text-align: center;
        vertical-align: middle;
        height: 8vh;
        width: 28vw;
        text-decoration: none;
        font-size: 3vh;
        border-top-left-radius: 2vh;
        border-top-right-radius: 2vh;
    }

    .nav-bar-item .active {
        background-color: white;
        color: black;
        transition: all 0.2s;
        transform: translateY(1vh);
        font-weight: bold;
    }
</style>
