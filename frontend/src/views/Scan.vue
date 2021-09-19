<template>
    <div v-swipe:left="navNext" v-swipe:right="navPrev" class="view">
        <!-- Camera Render -->
        <div class="camera-view">
            <qrcode-stream v-if="cameraRender" @decode="onDecode" @init="onInit" :track="paintOutline" :camera="camera">
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
        <div class="welcome" v-if="member">
            <div class="close-button" v-on:click="cancelMember">
                <i class="fas fa-times close-icon"/>
            </div>
            <div class="content">
                <span class="heading">Welcome</span>
                <span class="name">{{ member.first_name }}</span>
                <span class="icon">
                    <div v-if="memberIcon=='unknown'" class="icon-graphic status-unknown"><i class="fas fa-question"/></div>
                    <div v-else-if="memberIcon=='deceased'" class="icon-graphic status-deceased"><i class="fas fa-user-alt-slash"/></div>
                    <div v-else-if="memberIcon=='cancelled'" class="icon-graphic status-cancelled"><i class="fas fa-ban"/></div>
                    <div v-else-if="memberIcon=='pending'" class="icon-graphic status-pending"><i class="fas fa-hourglass-half"/></div>
                    <div v-else-if="memberIcon=='expired'" class="icon-graphic status-expired"><i class="fas fa-ban"/></div>
                    <div v-else-if="memberIcon=='grace'" class="icon-graphic status-grace"><i class="fas fa-hourglass-half"/></div>
                    <div v-else-if="memberIcon=='current'" class="icon-graphic status-current"><i class="fas fa-check-circle"/></div>
                    <div v-else-if="memberIcon=='new'" class="icon-graphic status-new"><i class="fas fa-plus-circle"/></div>
                    <span class="icon-text">Status: {{ member.status }}</span>
                </span>
                <span class="number">Membership # <code>{{ member.membership_num }}</code></span>
                
                <!-- Checkin Options (mutually exclusive) -->
                <div class="submit" v-if="submitType=='passive'">
                    <span v-for="event in events"
                        class="button button-ok"
                        v-on:click="submitAttendance(event, member)"
                        :key="event.pk"
                    >OK</span>
                </div>
                <div class="submit" v-else-if="submitType=='select'">
                    <span>What is {{ member.first_name }} attending?</span>
                    <span v-for="event in events"
                            class="button button-event"
                            v-on:click="submitAttendance(event, member)"
                            :key="event.pk"
                    >{{ event.title }}</span>
                </div>
                <div class="submit" v-else>
                    <span class="button button-subtle" v-on:click="forceMemberOK">Admit Anyway</span>
                </div>
                
            </div>
        </div>
    </div>
</template>

<script>
    import { QrcodeStream } from 'qrcode-reader-vue3'
    import ModalScreen from '../components/ModalScreen.vue'
    import axios from 'axios'

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
                error: "",
                result: "",
                resultType: null,
                members: [],  // Stack acquired from QR-Code, then member request
            }
        },
        computed: {
            cameraRender() {
                // Display camera if :
                //  - one or more events are selected
                //  - $store cameraDisplayEnabled
                return (
                    this.$store.state.events.selected.size &&
                    this.$store.state.cameraDisplayEnabled
                )
            },
            camera() {
                return this.$store.state.settings.cameraMode || 'auto'
            },
            member() {
                // First member on the stack
                return this.members ? this.members[0] : null
            },
            submitType() {
                // One of: {passive|select|none}
                if (this.member.status_isok) {
                    if (this.$store.state.events.selected.size == 1) {
                        return 'passive'
                    } else {
                        return 'select'
                    }
                }
                return 'none'
            },
            events() {
                return this.$store.getters.selectedEvents
            },
            memberIcon() {
                if (this.member) {
                    const status = this.member.status.toLowerCase()
                    return MEMBER_STATUS_MAP.includes(status) ? status : 'unknown'
                }
                return 'none'
            },
            settings() {
                return this.$store.settings
            },
        },
        methods: {
            // Navigation
            navPrev() { this.$router.push({name: 'Select'}) },
            navNext() { this.$router.push({name: 'List'}) },

            // QR-Code Scanner
            async onDecode(decoded) {
                this.result = decoded
                const memberNum = getMemberNumber(decoded)
                if (memberNum) { // looks like a member code, fetch!
                    // memberNum: {type: <contact|member>, number: <int>}
                    this.$store.commit('SET_LOADING', 'member', true);
                    const uri = `/api/members_${(memberNum.type === 'contact') ? 'cid' : 'memno'}/${memberNum.number}`
                    axios.get(uri).then(
                        (response) => {  // success
                            this.$store.commit('SET_LOADING', 'member', false);
                            this.members.push(response.data)
                            this.autoAdmitBegin(this.member) // new member
                        }
                    ).catch(
                        (error) => {  // failure
                            this.$store.commit('SET_LOADING', 'member', false);
                            // TODO: set error message
                        }
                    )
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
                if (!this.$store.state.settings.cameraOverlay) {
                    return
                }
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
            autoAdmitBegin(member) {
                // Auto-admit (if configured, and member is valid)
                const autoAdmitTime = this.$store.state.settings?.autoAdmitTime
                const eventCount = this.$store.state.events.selected.size
                if (member.status_isok && autoAdmitTime && (eventCount == 1) && (!member._autoAdmitTimeout)) { // else: requires manual
                    const event = this.events[0]  // record at start time (incase it changes)
                    member._autoAdmitTimeout = setTimeout(() => {
                        this.submitAttendance(event, member)
                    }, autoAdmitTime * 1000)
                }
            },
            autoAdmitCancel(member) {
                if (member?._autoAdmitTimeout) {
                    clearTimeout(member._autoAdmitTimeout)
                }
            },
            forceMemberOK() {
                // Force member's [cached] status as OK to admit
                const member = this.member
                member.status_isok = true
                this.autoAdmitBegin(member)
            },
            cancelMember() {
                // Cancel the admittance of member (pop member stack)
                this.autoAdmitCancel(this.member)
                this.members.shift()
            },
            submitAttendance(event, member) {
                this.autoAdmitCancel(member)
                axios.post('/api/attendance/', {
                    "csrfmiddlewaretoken": this.$store.getters.csrftoken,
                    "contact": member.contact_id,
                    "event": event.pk,
                }).then( // success
                    (response) => {
                        this.members.shift()
                        this.autoAdmitBegin(this.member) // next member (if any)
                    }
                ).catch( // failure
                    (error) => {
                        console.log('ERROR during attendance submission:', error)
                    }
                )
            },

            // Buttons
            buttonManual() {
                if (this.$store.state.events.selected.size) {
                    this.$store.dispatch('modalDisplayOpen', 'member-entry')
                }
            },
            buttonGuest() {
                if (this.$store.state.events.selected.size) {
                    this.$store.dispatch('modalDisplayOpen', 'guest-entry')
                }
            },
        },
    }
</script>

<style lang="scss" scoped>
    /* ----- Camera Render ----- */
    .camera-view {
        height: 60vh;
        width: 100vw;
        text-align: center;
        vertical-align: middle;

        .dialog {
            font-size: 5vw;
            padding: 40%;
            height: 100%;
            span { display: block; }
        }
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
    .welcome {
        position: absolute;
        width: 100vw;
        height: 100vh;
        top: 0;
        left: 0;
        background-color: rgba(50, 50, 50, 0.8);
        z-index: 2000;
        .content {
            background-color: aliceblue;
            width: 90vw;
            max-height: 90vh;
            margin: 3vh 5vw;
            border-radius: 3vh;
            padding: 5vh 3vw;
            text-align: center;
            overflow: auto;
        }
        span {
            display: block;
            font-size: 5vw;
        }
        .heading {
            font-weight: bold;
            font-size: 10vw;
        }
        .name {
            font-size: 8vw;
            margin: 0 0 2vh;
        }
        .number code {
            font-size: 7vw;
            font-weight: bold;
        }

        /* Membership Status Indicator Icon */
        .icon .icon-graphic {
            font-size: 30vw;
            margin: -0.25em 0;  /* remove inner padding (unknown origin)*/
        }
        .icon .icon-text {
            font-weight: bold;
            margin: 0 0 2vw;
        }
        // TODO: import membership status colours from common definition
        .status-deceased  { color: grey;       }
        .status-cancelled { color: red;        }
        .status-pending   { color: grey;       }
        .status-expired   { color: red;        }
        .status-grace     { color: grey;       }
        .status-current   { color: limegreen;  }
        .status-new       { color: grey;       }
        .status-unknown   { color: grey;       }  // set if status is anything else
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

    .submit {
        .button-ok {
            margin: 0 20%;
        }
        .button-event {
            margin: 0 0%;
            font-size: 4vw;
            width: unset;
            padding: 0.5em 2em;
            margin: 0.5em 0;
        }
        .button-subtle {
            margin: 0 20%;
            background-color: lightgrey;
            color: dodgerblue;
            border-color: dodgerblue;
            border-width: 0.5vw;
        }
    }
</style>
