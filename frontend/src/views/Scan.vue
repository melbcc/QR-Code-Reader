<template>
    <div v-swipe:left="navNext" v-swipe:right="navPrev">
        <h1>Scan Attendees</h1>
        <qrcode-stream v-if="cameraRender" @decode="onDecode" @init="onInit" :track="paintOutline">
            <div class="loading-indicator" v-if="loading">
                Loading...
            </div>
        </qrcode-stream>
        result: {{ result }}<br/>
        type: {{ resultType }}<br/>
        error: {{ error }}<br/>
        render: {{ cameraRender }}
    </div>
</template>

<script>
    import { QrcodeStream } from 'qrcode-reader-vue3'

    function getMemberNumber(decodedText) {
        if (typeof decodedText === 'string') {
            const match = decodedText.match(/(?<type>M)?(?<number>\d+)$/i);
            if (match) {
                return {
                    type: match.groups.type ? 'member' : 'contact',
                    number: parseInt(match.groups.number),
                }
            }
        }
    }

    export default {
        components: {
            QrcodeStream,
        },
        data() {
            return {
                loading: true,
                result: "",
                resultType: null,
                error: "",
            }
        },
        computed: {
            cameraRender() {
                return this.$store.state.cameraDisplayEnabled;
            },
        },
        methods: {
            navPrev() { this.$router.push('/select') },
            navNext() { this.$router.push('/list') },
            async onDecode(decoded) {
                this.result = decoded;
            },
            async onInit (promise) {
                // Error Lokup:
                // https://gruhn.github.io/vue-qrcode-reader/api/QrcodeStream.html#events
                try {
                    await promise;
                } catch (error) {
                    this.error = error.name;
                } finally {
                    this.loading = false;
                }
            },
            paintOutline (detectedCodes, ctx) {
                // copied from: https://gruhn.github.io/vue-qrcode-reader/demos/CustomTracking.html
                for (const detectedCode of detectedCodes) {
                    const [ firstPoint, ...otherPoints ] = detectedCode.cornerPoints;
                    const { boundingBox, rawValue } = detectedCode;
                    const memberNum = getMemberNumber(rawValue);

                    // Component Data
                    this.resultType = (memberNum ? memberNum.type : "invalid").toUpperCase();

                    // Boundary Line
                    ctx.strokeStyle = memberNum ? "dodgerblue" : "red";
                    ctx.lineWidth = boundingBox.width / 20;

                    ctx.beginPath();
                    ctx.moveTo(firstPoint.x, firstPoint.y);
                    for (const { x, y } of otherPoints) {
                        ctx.lineTo(x, y);
                    }
                    ctx.lineTo(firstPoint.x, firstPoint.y);
                    ctx.closePath();
                    ctx.stroke();

                    // Floating Text
                    const centerX = boundingBox.x + boundingBox.width / 2;
                    const centerY = boundingBox.y + boundingBox.height / 2;
                    const fontSize = Math.max(12, 50 * boundingBox.width / ctx.canvas.width);

                    ctx.font = `bold ${fontSize}px sans-serif`;
                    ctx.textAlign = 'center';

                    ctx.lineWidth = boundingBox.width / 30;
                    ctx.strokeText(this.resultType, centerX, centerY);

                    ctx.fillStyle = 'white';
                    ctx.fillText(this.resultType, centerX, centerY)
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
