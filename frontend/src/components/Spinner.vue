<template>
    <div class="spinner" :class="spinnerClass">
        <i class="fas fa-sync icon" />
    </div>
</template>

<script>
    export default {
        props: {
            loadkey: String,
        },
        computed: {
            spinnerClass() {
                return this.$store.state.loading[this.loadkey] ? 'rotating' : '';
            },
        },
    }
</script>

<style scoped>
    .spinner {
        float: right;
        margin-right: 1vh;
        width: 5vh;
        height: 5vh;
        border-radius: 50%;
        background-color: dodgerblue;
        cursor: pointer;
        font-size: 3vh;
        color: white;
        text-align: center;
        vertical-align: middle;
    }
    .spinner .icon {
        height: 100%;
    }
    .spinner.rotating {
        -webkit-animation:spin 1s linear infinite;
        -moz-animation:spin 1s linear infinite;
        animation:spin 1s linear infinite;
    }
    @-moz-keyframes spin { 100% { -moz-transform: rotate(360deg); } }
    @-webkit-keyframes spin { 100% { -webkit-transform: rotate(360deg); } }
    @keyframes spin { 100% { -webkit-transform: rotate(360deg); transform:rotate(360deg); } }
</style>