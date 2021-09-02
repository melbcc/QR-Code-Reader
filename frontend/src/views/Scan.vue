<template>
    <div v-swipe:left="navNext" v-swipe:right="navPrev" class="view">
        <!-- Camera Render -->
        <div class="camera-view">
            <qrcode-stream v-if="cameraRender" @decode="onDecode" @init="onInit" :track="paintOutline">
                <div class="dialog" v-if="loading">
                    Loading...
                </div>
            </qrcode-stream>
            <div v-else class="dialog">
                <span>Disabled</span>
            </div>
        </div>
        <!-- Manual Selection Buttons -->
        <div>
            <div class="button" v-on:click="buttonGuest"><i class="fas fa-user"/> Guest</div>
            <div class="button" v-on:click="buttonManual"><i class="fas fa-keyboard"/> Manual</div>
        </div>

        <!-- Modal : Member Number Entry -->
        <ModalScreen name="member-entry">
            <h2>Member Entry</h2>
        </ModalScreen>

        <!-- Modal : Guest Entry -->
        <ModalScreen name="guest-entry">
            <h2>Guest Entry</h2>
        </ModalScreen>

        <!-- Modal : Welcome Message -->
        <ModalScreen name="welcome-message">
            <h2>Welcome {{ member.first_name }}</h2>
            <p>Membership Number: {{ member.membership_num }}</p>
            <p>Contact ID: {{ member.contact_id }}</p>
            <p>Status: {{ member.status }}</p>
            <p>{{ member }}</p>
        </ModalScreen>
    </div>
</template>

<script>
    import { QrcodeStream } from 'qrcode-reader-vue3'
    import ModalScreen from '../components/ModalScreen.vue'

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
            ModalScreen,
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
                return this.$store.state.cameraDisplayEnabled
            },
            member() {
                return this.$store.state.member
            },
        },
        methods: {
            navPrev() { this.$router.push('/select') },
            navNext() { this.$router.push('/list') },
            async onDecode(decoded) {
                this.result = decoded
                this.$store.dispatch('fetchMember', getMemberNumber(decoded))
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
            buttonManual() {
                this.$store.dispatch('modalDisplayOpen', 'member-entry')
            },
            buttonGuest() {
                this.$store.dispatch('modalDisplayOpen', 'guest-entry')
            },
        },
    }
</script>

<style scoped>
    .camera-view {
        height: 60vh;
        width: 100vw;
        text-align: center;
        vertical-align: middle;
    }

    .camera-view .dialog {
        font-size: 5vw;
        padding: 40%;
        height: 100%;
    }

    .button {
        display: inline-block;
        text-align: center;
        vertical-align: middle;
        width: 44vw;
        font-size: 4vw;
        background-color: dodgerblue;
        color: white;
        border-radius: 3vw;
        margin: 2vh 3vw 0 3vw;
        padding: 2vh 0;
        cursor: pointer;
        font-weight: bold
    }
    

</style>
