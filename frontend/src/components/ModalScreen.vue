<template>
    <div class="modal" v-if="isActive">
        <div class="close-button" v-on:click="clickClose">
            <i class="fas fa-times close-icon"/>
        </div>
        <div class="content">
            <slot />
        </div>
    </div>
</template>

<script>
    export default {
        props: {
            name: String,
        },
        computed: {
            isActive() {
                return this.$store.state.modal === this.name;
            }
        },
        methods: {
            clickClose() {
                this.$store.dispatch('modalDisplayOpen', null)
            }
        },
    }
</script>

<style lang="scss" scoped>
    /* Fullscreen Modal Content */
    .modal {
        position: absolute;
        width: 100vw;
        height: 100vh;
        top: 0;
        left: 0;
        background-color: rgba(50, 50, 50, 0.8);
        /*display: none;*/
        z-index: 2000;
        .content {
            background-color: aliceblue;
            width: 90vw;
            max-height: 80vh;
            margin: 4vh 5vw;
            border-radius: 3vh;
            padding: 1em 1em 2em;
            text-align: center;
            overflow: auto;
        }
        &.active {
            display: unset;
        }
    }

    /* Close Button */
    .close-button {
        position: absolute;
        top: 1vh;
        right: 1vh;
        width: 6vh;
        height: 6vh;
        border-radius: 50%;
        background-color: red;
        z-index: 1000;
        text-align: center;
        vertical-align: middle;
        cursor: pointer;
        transition: all 0.75s;
        .close-icon {
            font-size: 4vh;
            color: white;
            height: 100%;
        }
    }
</style>