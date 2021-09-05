<template>
    <div v-swipe:left="navNext" v-swipe:right="navPrev" class="view">
        <!-- Camera Render -->
        <div class="camera-view">
            <qrcode-stream v-if="cameraRender" @decode="onDecode" @init="onInit" :track="paintOutline">
                <div class="dialog" v-if="loading">
                    <i class="fas fa-camera"/> Loading...
                </div>
            </qrcode-stream>
            <div v-else class="dialog">
                <span><i class="fas fa-power-off"/> Disabled</span>
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
            <div class="welcome">
                <span class="heading">Welcome </span>
                <span class="name">{{ member.first_name }}</span>
                <span class="icon" :class="memberIconClass">
                    <div class="icon-graphic status-deceased"><i class="fas fa-user-alt-slash"/></div>
                    <div class="icon-graphic status-cancelled"><i class="fas fa-ban"/></div>
                    <div class="icon-graphic status-pending"><i class="fas fa-hourglass-half"/></div>
                    <div class="icon-graphic status-expired"><i class="fas fa-ban"/></div>
                    <div class="icon-graphic status-grace"><i class="fas fa-hourglass-half"/></div>
                    <div class="icon-graphic status-current"><i class="fas fa-check-circle"/></div>
                    <div class="icon-graphic status-new"><i class="fas fa-plus-circle"/></div>
                    <div class="icon-graphic status-unknown"><i class="fas fa-question"/></div>
                    <span class="icon-text">Status: {{ member.status }}</span>
                </span>
                <span class="number">Membership # <code>{{ member.membership_num }}</code></span>
                <!--<span>Contact ID: {{ member.contact_id }}</span>-->
                <!-- <span>{{ member }}</span> -->
            </div>
        </ModalScreen>
    </div>
</template>

<script>
    import { QrcodeStream } from 'qrcode-reader-vue3'
    import ModalScreen from '../components/ModalScreen.vue'

    function getMemberNumber(decodedText) {
        // Get member number from decoded QR-Code text
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
    // Supported member.status values (lower-case)
    //  (all others will be styled as "unknown")
    const MEMBER_STATUS_MAP = [
        'deceased',
        'cancelled',
        'pending',
        'expired',
        'grace',
        'current',
        'new',
    ]

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
            cameraRender() { return this.$store.state.cameraDisplayEnabled },
            member() { return this.$store.state.member },
            memberIconClass() {
                const memberStatus = (this.$store.state.member?.status || '').toLowerCase()
                if (!memberStatus) {
                    return 'status-none'
                } else if (MEMBER_STATUS_MAP.includes(memberStatus)) {
                    return 'status-' + memberStatus
                } else {
                    return 'status-unknown'
                }
            },
        },
        methods: {
            navPrev() { this.$router.push({name: 'Select'}) },
            navNext() { this.$router.push({name: 'List'}) },
            async onDecode(decoded) {
                this.result = decoded
                const memberNum = getMemberNumber(decoded)
                if (memberNum) {
                    this.$store.dispatch('fetchScannedMember', getMemberNumber(decoded))
                }
            },
            async onInit (promise) {
                // Error Lokup:
                // https://gruhn.github.io/vue-qrcode-reader/api/QrcodeStream.html#events
                this.loading = true;
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
                    const { cornerPoints, boundingBox, rawValue } = detectedCode;
                    const memberNum = getMemberNumber(rawValue);

                    // Component Data
                    this.resultType = (memberNum ? memberNum.type : "invalid").toUpperCase();

                    // Boundary Line
                    ctx.strokeStyle = memberNum ? "dodgerblue" : "red";
                    ctx.lineWidth = boundingBox.width / 20;

                    ctx.beginPath();
                    ctx.moveTo(...Object.values(cornerPoints[cornerPoints.length-1]));  // last
                    cornerPoints.forEach((point) => ctx.lineTo(...Object.values(point)))
                    ctx.closePath();
                    ctx.stroke();

                    // Floating Text
                    const fontSize = Math.max(32, 200 * (boundingBox.width / ctx.canvas.width));
                    const centerX = (cornerPoints[0].x + cornerPoints[2].x) / 2
                    const centerY = (cornerPoints[0].y + cornerPoints[2].y) / 2 + (fontSize / 3)

                    ctx.font = `bold ${fontSize}px sans-serif`;
                    ctx.textAlign = 'center';

                    ctx.lineWidth = boundingBox.width / 10;
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
    /* ----- Camera Render ----- */
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

    /* ----- Buttons ----- */
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
    
    /* ----- Welcome Message -----*/
    .welcome span {
        display: block;
        font-size: 5vw;
    }
    .welcome .heading {
        font-weight: bold;
        font-size: 10vw;
    }
    .welcome .name {
        font-size: 8vw;
        margin: 0 0 2vh;
    }
    .welcome .number code {
        font-size: 7vw;
        font-weight: bold;
    }

    /* Membership Status Indicator Icon */
    .welcome .icon .icon-graphic {
        font-size: 30vw;
        margin: -0.25em 0;  /* remove inner padding (unknown origin)*/
    }
    .welcome .icon .icon-text {
        font-weight: bold;
        margin: 0 0 2vw;
    }
    .welcome .status-deceased  { color: grey;       }
    .welcome .status-cancelled { color: red;        }
    .welcome .status-pending   { color: grey;       }
    .welcome .status-expired   { color: red;        }
    .welcome .status-grace     { color: grey;       }
    .welcome .status-current   { color: limegreen;  }
    .welcome .status-new       { color: grey;       }
    .welcome .status-unknown   { color: grey;       }  /* set if status is anything else */

    /* hide non-selected icons */
    .welcome .icon.status-deceased    .icon-graphic:not(.status-deceased)   { display: none; }
    .welcome .icon.status-cancelled   .icon-graphic:not(.status-cancelled)  { display: none; }
    .welcome .icon.status-pending     .icon-graphic:not(.status-pending)    { display: none; }
    .welcome .icon.status-expired     .icon-graphic:not(.status-expired)    { display: none; }
    .welcome .icon.status-grace       .icon-graphic:not(.status-grace)      { display: none; }
    .welcome .icon.status-current     .icon-graphic:not(.status-current)    { display: none; }
    .welcome .icon.status-new         .icon-graphic:not(.status-new)        { display: none; }
    .welcome .icon.status-unknown     .icon-graphic:not(.status-unknown)    { display: none; }
    .welcome .icon.status-none        .icon-graphic { display: none; }  /* hide all */
</style>
