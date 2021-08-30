<template>
  <div class="event" :class="selectedClass" v-on:click="clickEvent">
    <span class="icon">
      <i class="unsel far fa-circle" />
      <i class="sel   fas fa-check-circle" />
    </span> {{ title }}
  </div>
</template>

<script>
  export default {
    
    props: {
      title: String,
      pk: Number,
    },
    computed: {
      selectedClass() {
        return this.$store.state.events.selected.has(this.pk) ? 'selected' : 'not-selected';
      },
    },
    methods: {
      clickEvent() {
        this.$store.commit('TOGGLE_EVENT_PK', this.pk);
      },
    },
  }
</script>

<style scoped>
  .event {
    display: block;
    border-radius: 30px;
    border-color: grey;
    border-width: 2px;
    border-style: solid;
    background-color: white;
    margin: 0.2em;
    padding: 0.5em 1em;
    font-size: 1.5em;
  }

  .event.selected {
    background-color: dodgerblue;
    border-color: dodgerblue;
    color: white;
  }

  /* Selection indicator icon : toggle */
  .event.selected .icon .sel       { display: inline-block }
  .event.selected .icon .unsel     { display: none }
  .event.not-selected .icon .sel   { display: none }
  .event.not-selected .icon .unsel { display: inline-block }

</style>
