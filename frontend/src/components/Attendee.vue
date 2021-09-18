<template>
    <div class="attendee">
        <span class="fullname">{{ obj.contact.first_name }} {{ obj.contact.last_name }}</span>
        <span class="sync-status">
            <div v-if="obj.export_time"><i class="fas fa-check-circle"/></div>
            <div v-else><i class="far fa-check-circle"/></div>
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
        .sync-status {
            float: right;
            margin-right: 0.5em;
        }
    }
</style>