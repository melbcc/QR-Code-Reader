<template>
    <div class="attendee">
        <span class="fullname">{{ obj.contact.first_name }} {{ obj.contact.last_name }}</span>
        <span class="sync-status">
            <div v-if="obj.export_time"><i class="fas fa-check-circle"/></div>
            <div v-else><i class="far fa-check-circle"/></div>
        </span>
        <span class="membership-status">
            <div v-if="obj.contact.membership?.status=='Deceased'" class="icon-graphic status-deceased"><i class="fas fa-user-alt-slash"/></div>
            <div v-else-if="obj.contact.membership?.status=='Cancelled'" class="icon-graphic status-cancelled"><i class="fas fa-ban"/></div>
            <div v-else-if="obj.contact.membership?.status=='Pending'" class="icon-graphic status-pending"><i class="fas fa-hourglass-half"/></div>
            <div v-else-if="obj.contact.membership?.status=='Expired'" class="icon-graphic status-expired"><i class="fas fa-ban"/></div>
            <div v-else-if="obj.contact.membership?.status=='Grace'" class="icon-graphic status-grace"><i class="fas fa-hourglass-half"/></div>
            <div v-else-if="obj.contact.membership?.status=='Current'" class="icon-graphic status-current"><i class="fas fa-check-circle"/></div>
            <div v-else-if="obj.contact.membership?.status=='New'" class="icon-graphic status-new"><i class="fas fa-plus-circle"/></div>
            <div v-else class="icon-graphic status-unknown"><i class="fas fa-question"/></div>
        </span>
    </div>
</template>

<script>
    export default {
        props: {
            obj: Object,
        },
        data() {
            return {
            }
        },
    }
</script>

<style lang="scss" scoped>
    .attendee {
        font-size: 1.5em;
        .membership-status {
            float: right;
            margin-right: 0.5em;
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
        .sync-status {
            float: right;
            margin-right: 0.5em;
            color: dodgerblue;
        }
    }
</style>