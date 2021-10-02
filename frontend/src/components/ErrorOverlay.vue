<template>
    <div class="error-msg" v-if="message || title">
        <div class="content">
            <h2>{{ title }}</h2>
            <div class="message">{{ message }}</div>
            <div class="button" v-on:click="close">Close <i class="fas fa-times"/></div>
        </div>

    </div>
</template>

<script>
    export default {
        computed: {
            title() { return this.$store.state.error.title },
            message() { return this.$store.state.error.message },
        },
        methods: {
            close() {
                this.$store.commit('CLEAR_ERROR')
            },
        },
    }
</script>

<style lang="scss" scoped>
    .error-msg {
        position: fixed;
        display: block;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 90%);
        z-index: 2000;

        padding: 1.5em 2em;
        font-size: 1.2em;

        .content {
            border-style: dashed;
            border-color: red;
            border-width: 0.3em;
            border-radius: 2em;
            //height: calc(100% - 20em);
            padding: 1.5em 2em;

            font-family: monospace;
            text-align: center;
            color: white;

            h2 {
                color: white;
            }
            .message {
                padding: 1em 0;
                text-align: left;
            }
            .button {
                font-size: 1.5em;
                border-radius: 2em;
                padding: 0.5em 2em;
                width: unset;
                background: darkred;
                
            }
        }
    }
</style>
