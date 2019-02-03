/* ========== Basic Navigation =========== */
function jumpTo(h) {
    // ref: https://stackoverflow.com/questions/13735912/#13736194
    var url = location.href;
    location.href = "#" + h;
    history.replaceState(null, null, url);
}


/* ========== Local REST ========== */
const getMember = async (contact_id) => {
    // Clean up ID
    // be tollerant of noise (like that from the QR code)
    contact_id = contact_id.match(/\d*$/)[0];
    // TODO: accept only a pure number, or a fully qualified URL.
    //       otherwise return null

    // Send Query
    const response = await fetch('/api/members/' + contact_id + '/');

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
const resetPage = async () => {
    // Body Text
    $('span.first_name').text('');
    $('span.last_name').text('');
    $('span.status_name').text('');
    $('span.event_name').text('');

    /* Clear Form Data */
    // Scan
    $('#scanform input[name=contact_id]').val('');
    // Guest
    $('#guestform input[type=text]').val('');
    // Event Selection
    $('#eventform input[type=radio]').prop('checked', false);

    // Attendance hidden form (in "saving" state)
    $('#attendanceform input[name=member_pk]').val('');
    $('#attendanceform input[name=event_pk]').val('');

    /* Move to top */
    jumpTo("scan");

    /* Focus Scan Input */
    $('#scanform input[name=contact_id]').focus();
}

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
        $('#attendanceform input[name=member_pk]').val(member_obj['pk']);
    } else {
        resetPage();
        // Do nothing; just reset the page
        return;
    }

    if (g_events.length > 1) {
        jumpTo("events");
    } else {
        $('span.event_name').text(g_events[0]['title'])
        $('#attendanceform input[name=event_pk]').val(g_events[0]['pk']);
        jumpTo("saving");
        saveAttendance(member_obj['pk'], g_events[0]['pk']);
    }
}

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
        $('#attendanceform input[name=event_pk]').val(event_pk);
    }

    jumpTo("saving");
    saveAttendance($('#attendanceform input[name=member_pk]').val(), event_pk);
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
}
