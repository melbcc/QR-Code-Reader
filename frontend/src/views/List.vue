<template>
  <div v-swipe:right="navPrev">
    <h1>List Attendees</h1>
    <a-button type="primary" @click="showModal">Click Me</a-button>
  </div>
  <a-modal
    :visible="visible"
    title="Basic Modal"
    @ok="hideModal"
  >
    <p>Thanks for clicking.</p>
    <p>Please click OK to close.</p>
  </a-modal>
</template>

<script>
  export default {
    methods: {
      navPrev() { this.$router.push('/scan') },
      showModal() { this.visible = true },
      hideModal() { this.visible = false },
    },
    data() {
      return {
        visible: false,
      }
    },
  }
</script>

<style scoped>
</style>
