/* ========== Basic Navigation =========== */
const defaultFormMap = {
    "scan": '#scanform input[name=contact_id]',
    "signin_guest": '#guestform input[name=first_name]',
    "signin_memno": '#memnumform input[name=membership_num]'
};

const jumpTo = (h) => {
    resetPage.cb_pending = false;

    // ref: https://stackoverflow.com/questions/13735912/#13736194
    var url = location.href;
    window.location.replace('#' + h);

    // Focus on input depending on page:
    var focusElementCSS = defaultFormMap[h];
    if (focusElementCSS !== undefined) {
        $(focusElementCSS).focus();
    }
}

jumpTo.in = (h, timeout_ms) => {
    setTimeout(() => {
        jumpTo(h);
    }, timeout_ms);
}

/* ========== Local REST ========== */
const getMember = async (contact_id) => {
    // Clean up ID
    // be tollerant of noise (like that from the QR code)
    contact_id = contact_id.match(/\d*$/)[0];
    // TODO: accept only a pure number, or a fully qualified URL.
    //       otherwise return null

    // Send Query
    const response = await fetch('/api/members_cid/' + contact_id + '/');

    // Return Member object or null
    var member_obj = null;
    if (response.status == 200) {
        member_obj = await response.json(); //extract JSON from the http response;
    }

    console.log(member_obj);
    return member_obj;
}


const getEvent = async (pk) => {
    // Send Query
    const response = await fetch('/api/events/' + pk + '/');

    // Return Event object or null
    var event_obj = null;
    if (response.status == 200) {
        event_obj = await response.json(); //extract JSON from the http response;
    }

    console.log(event_obj);
    return event_obj;
}


const getLocationList = async () => {
    // Lists all locations (pull from REST)
    const response = await fetch('/api/locations/');

    // Extract location list from response
    var locations = null;
    if (response.status == 200) {
        locations = await response.json();
    }

    console.log(locations);
    return locations;
}


/* ========== Event Handlers ========== */
/* ----- Reset ----- */
const resetPage = async () => {
    // Body Text
    $('span.first_name').text('');
    $('span.last_name').text('');
    $('span.status_name').text('');
    $('span.event_name').text('');

    /* Clear Form Data */
    // Event Selection
    $('#eventform input[type=radio]').prop('checked', false);
    // Scan
    $('#scanform input[type=text]').val('');
    // Guest
    $('#guestform input[type=text]').val('');
    // Membership Number
    $('#memnumform input[type=text]').val('');

    // Attendance hidden form (in "saving" state)
    $('#attendanceform input[name=contact_id]').val('');
    $('#attendanceform input[name=event_pk]').val('');

    /* Move to top */
    console.log(g_events);
    if (g_events.length > 1) {
        jumpTo("events"); // Select which event you're attending
    } else {
        jumpTo("scan"); // Only one event, just scan in
    }
}

resetPage.in = (timeout_ms) => {
    resetPage.cb_pending = true;
    setTimeout(() => {
        if (resetPage.cb_pending) {
            resetPage.cb_pending = false;
            resetPage();
        }
    }, timeout_ms);
}

resetPage.cb_pending = false; // callback pending (used to cancel reset)

/* ----- Scan contact_id ----- */
const submitScan = async () => {
    /* Run when submitting the QR-Code */
    // Get member
    var qrtext = $('#scanform input[name=contact_id]').val();
    const member_obj = await getMember(qrtext);

    if (member_obj) {
        // Inform user of status
        $('span.first_name').text(member_obj['first_name']);
        $('span.last_name').text(member_obj['last_name']);
        $('span.status_name').text(member_obj['status']);
        // Set Member for attendance record
        $('#attendanceform input[name=contact_id]').val(member_obj['contact_id']);
    } else {
        resetPage();
        // Do nothing; just reset the page
        return;
    }

    if (g_events.length > 1) {
        // Play sound
        $('#sound_scan')[0].play();
        if ($('#eventform input[name=event]:checked').length) {
            // Event has already been selected
            submitEvent();
        } else {
            jumpTo("events");
        }
    } else {
        $('span.event_name').text(g_events[0]['title'])
        $('#attendanceform input[name=event_pk]').val(g_events[0]['pk']);
        // Play Sound
        if (member_obj['status_isok']) {
            $('#sound_scan')[0].play();
        } else {
            $('#sound_badmember')[0].play();
        }
        jumpTo("saving");
        saveAttendance(member_obj['pk'], g_events[0]['pk']);
    }
}

/* -----  ----- */
const submitEvent = async () => {
    // Get Selected Event
    var event_id = $('#eventform input[name=event]:checked').prop('id');
    if (event_id === undefined) {
        // no event was selected, do nothing
        return;
    }

    // Get Event Object
    var event_pk = event_id.match(/\d+$/)[0];
    var event_obj = await getEvent(event_pk);
    if (event_obj) { // just checking it exists
        $('span.event_name').text(event_obj['title']);
        $('#attendanceform input[name=event_pk]').val(event_pk);
    }

    // Get Member Data
    var member_obj = await getMember($('#attendanceform input[name=contact_id]').val());

    if (member_obj['status_isok']) {
        //$('#sound_scan')[0].play();
    } else {
        $('#sound_badmember')[0].play();
    }

    jumpTo("saving");
    saveAttendance(member_obj['pk'], event_pk);
}

const saveAttendance = (member_pk, event_pk) => {
    // Submit Attendance to REST API
    attendance_obj = {
        "csrfmiddlewaretoken": $('#attendanceform input[name=csrfmiddlewaretoken]').val(),
        "member": member_pk,
        "event": event_pk
    }
    console.log(attendance_obj);

    $.post(
        "/api/attendance/",
        attendance_obj,
        (data) => {
            console.log(data);
        }
    );

    // Get
    jumpTo("welcome");
    resetPage.in(3000); // 3 seconds
}
