<template>
  <div v-swipe:left="navNext" v-swipe:right="navPrev">
    <h1>Scan Attendees</h1>
    <qrcode-stream @decode="onDecode" @init="onInit" :track="paintOutline">
      <div class="loading-indicator" v-if="loading">
        Loading...
      </div>
    </qrcode-stream>
    result: {{ result }}<br/>
    {{ error }}
  </div>
</template>

<script>
  import { QrcodeStream } from 'qrcode-reader-vue3'
  export default {
    components: {
      QrcodeStream,
    },
    data() {
      return {
        loading: true,
        result: "",
        error: "",
      }
    },
    methods: {
      navPrev() { this.$router.push('/select') },
      navNext() { this.$router.push('/list') },
      async onDecode(decoded) {
        this.result = decoded
      },
      async onInit (promise) {
        // Error Lokup:
        // https://gruhn.github.io/vue-qrcode-reader/api/QrcodeStream.html#events
        try {
          await promise
        } catch (error) {
          this.error = error.name
        } finally {
          this.loading = false
        }
      },
      paintOutline (detectedCodes, ctx) {
        // copied from: https://gruhn.github.io/vue-qrcode-reader/demos/CustomTracking.html
        for (const detectedCode of detectedCodes) {
          const [ firstPoint, ...otherPoints ] = detectedCode.cornerPoints

          ctx.strokeStyle = "red";

          ctx.beginPath();
          ctx.moveTo(firstPoint.x, firstPoint.y);
          for (const { x, y } of otherPoints) {
            ctx.lineTo(x, y);
          }
          ctx.lineTo(firstPoint.x, firstPoint.y);
          ctx.closePath();
          ctx.stroke();
        }
      },
    },
  }
</script>

<style scoped>
  .qrcode-stream-wrapper {
    height: 60vh;
    width: 100vw;
  }
</style>
