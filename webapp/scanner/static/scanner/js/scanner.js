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

jumpTo.withTimeout = (h, timeout_ms) => {
    setTimeout(() => {
        jumpTo(h);
    }, timeout_ms);
}


/* ========== Multimedia =========== */
const playSound = (element_id) => {
    $('#' + element_id)[0].play();
}

playSound.withTimeout = (element_id, timeout_ms) => {
    setTimeout(() => {
        playSound(element_id);
    }, timeout_ms);
}

/* ========== Local REST ========== */
/* ----- Member ----- */
const getMember = async (contact_id, membership_num) => {
    var response;
    if (contact_id !== undefined) {
        // Clean up ID
        // be tollerant of noise (like that from the QR code)
        contact_id = contact_id.toString();
        contact_id = contact_id.match(/\d*$/)[0];
        // TODO: accept only a pure number, or a fully qualified URL.
        //       otherwise return null

        // Send Query
        response = await fetch('/api/members_cid/' + contact_id + '/');
    } else {
        // Send Query
        membership_num = membership_num.toString();
        response = await fetch('/api/members_memno/' + membership_num + '/');
    }

    // Return Member object or null
    var member_obj = null;
    if (response.status == 200) {
        member_obj = await response.json(); //extract JSON from the http response;
    }

    console.log(member_obj);
    return member_obj;
}

getMember.byContactID = (contact_id) => {return getMember(contact_id, undefined);}
getMember.byMemberNum = (membership_num) => {return getMember(undefined, membership_num);}


/* ----- Event ----- */
const getEvent = async (pk) => {
    // Send Query
    const response = await fetch('/api/events/' + pk.toString() + '/');

    // Return Event object or null
    var event_obj = null;
    if (response.status == 200) {
        event_obj = await response.json(); //extract JSON from the http response;
    }

    console.log(event_obj);
    return event_obj;
}


/* ----- Location ----- */
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

    // Save error message
    $('span.error_msg').text('');
    // Attendance hidden form (in "saving" state)
    $('#attendanceform input[name=member_pk]').val('');
    $('#attendanceform input[name=event_pk]').val('');

    /* Move to top */
    jumpTo("events");
    if (g_events.length == 1) {
        submitEvent();
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

/* ----- Event Selected ----- */
const submitEvent = async () => {
    // Get Selected (or only) Event
    var event_obj;
    if (g_events.length > 1) { // Multiple events, 1 must be selected
        // Get selected event pk
        var event_id = $('#eventform input[name=event]:checked').prop('id');
        if (event_id === undefined) {
            resetPage(); // no event was selected, reset for good measure
            return;
        }

        // Get Event Object
        var event_pk = event_id.match(/\d+$/)[0];
        event_obj = await getEvent(event_pk);

    } else {
        // Only 1 event configured
        event_obj = await getEvent(g_events[0]['pk']);
    }

    // Set page content baesd on Event
    if (event_obj) { // confirm event exists
        $('span.event_name').text(event_obj['title']);
        $('#attendanceform input[name=event_pk]').val(event_obj['pk']);
    }

    jumpTo("scan");
}

/* ----- Member identified ----- */
const continueWithMember = (member) => {
    // param: member = object as returned by getMember()
    // Inform user of status
    $('span.first_name').text(member['first_name']);
    $('span.last_name').text(member['last_name']);
    $('span.status_name').text(member['status']);
    // Set Member for attendance record
    $('#attendanceform input[name=member_pk]').val(member['pk']);

    // Play Sound
    if (member['status_isok']) {
        playSound('sound_scan');
    } else {
        playSound('sound_error');
    }

    // Record Attendance
    jumpTo("saving");
    saveAttendance.fromForm();
}

/* ----- Scan contact_id ----- */
const submitScan = async () => {
    /* Run when submitting the QR-Code */
    // Get member
    var qrtext = $('#scanform input[name=contact_id]').val();
    const member_obj = await getMember.byContactID(qrtext);

    if (!member_obj) {
        resetPage();
        // Do nothing; just reset the page
        return;
    }

    continueWithMember(member_obj);
}

/* ----- Membership Number ----- */
const submitMemberNumber = async () => {
    // Get member (by their membership number)
    var membership_num = $('#memnumform input[name=membership_num]').val();
    const member_obj = await getMember.byMemberNum(membership_num);

    if (!member_obj) {
        resetPage();
        // Do nothing; just reset the page
        return;
    }

    continueWithMember(member_obj);
}


const saveAttendance = (member_pk, event_pk) => {
    // Submit Attendance to REST API
    attendance_obj = {
        "csrfmiddlewaretoken": $('#attendanceform input[name=csrfmiddlewaretoken]').val(),
        "member": member_pk,
        "event": event_pk
    }
    console.log(attendance_obj);

    var response = $.post(
        "/api/attendance/",
        attendance_obj,
        (data) => {
            console.log(data);
        }
    ).then(
        (value) => { // success
            jumpTo("welcome");
            resetPage.in(3000); // 3 seconds
        },
        (reason) => { // failure
            $('span.error_msg').text(reason.responseText);
            console.error(reason);
            playSound('sound_error');
            resetPage.in(3000); // 3 seconds
        }
    );
}

saveAttendance.fromForm = () => {
    saveAttendance(
        $('#attendanceform input[name=member_pk]').val(),
        $('#attendanceform input[name=event_pk]').val()
    );
}
