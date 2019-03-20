var err_lastActiveElement = undefined;

/* ========== Keyboard, Numpad & Callbacks =========== */
// Guest Keyboard
var keyboard_guest;
var selectedInput_guest;
var shortShift_guest = false;

function onChange_guest(input) {
    document.querySelector(selectedInput_guest || ".input").value = input;
}

function onKeyPress_guest(button) {
    // Shift & Caps
    if (button === "{shift}") {
        shortShift_guest = !shortShift_guest;
        handleShift_guest();
    } else if (button === "{lock}") {
        handleShift_guest();
    } else if (shortShift_guest) {
        shortShift_guest = false;
        handleShift_guest();
    }

    // Submit
    if (button === "{enter}") {
        $('#guestform').submit();
    }
}

function handleShift_guest() {
    let currentLayout = keyboard_guest.options.layoutName;
    let shiftToggle = currentLayout === "default" ? "shift" : "default";

    keyboard_guest.setOptions({
        layoutName: shiftToggle
    });
}

function onInputFocus_guest(event) {
    selectedInput_guest = `#${event.target.id}`;

    keyboard_guest.setOptions({
        inputName: event.target.id
    });
}

function onInputChange_guest(event) {
    keyboard_guest.setInput(event.target.value, event.target.id);
}

// Membership Number Numpad
var keyboard_memnum;

function onChange_memnum(input) {
    document.querySelector("#memnumform input[name='membership_num']").value = input;
}

function onKeyPress_memnum(button) {
    // Submit
    if (button === "{enter}") {
        $('#memnumform').submit();
    }
}


/* ========== Setup =========== */
const setupScannerPage = () => {
    // Bind Events
    $('.reset-button').click(() => {
        resetPage();
    });
    $('.error-dialog').click(() => {
        /* If an event triggers both resetPage(), and errorReset(),
         * there's little guarentee for which will be called first (I think).
         * To ensure resetPage() is called first, a small delay is set
         */
        errorReset.in(50);
    });

    // Keyboard - Guest
    let Keyboard = window.SimpleKeyboard.default;

    keyboard_guest = new Keyboard("#signin_guest .simple-keyboard", {
        onChange: input => onChange_guest(input),
        onKeyPress: button => onKeyPress_guest(button),
        buttonTheme: [
            {
              class: "hg-submit",
              buttons: "{enter}",
            },
        ],
    });

    document.querySelectorAll("#guestform input").forEach(input => {
        input.addEventListener("focus", onInputFocus_guest);
        // Optional: Use if you want to track input changes
        // made without simple-keyboard
        input.addEventListener("input", onInputChange_guest);
    });

    document.querySelector("#guestform input").addEventListener("input", event => {
        keyboard_guest.setInput(event.target.value);
    });

    // Keyboard - Numpad
    keyboard_memnum = new Keyboard("#signin_memno .simple-keyboard", {
        onChange: input => onChange_memnum(input),
        onKeyPress: button => onKeyPress_memnum(button),
        layout: {
            default: ["1 2 3", "4 5 6", "7 8 9", "{bksp} 0 {enter}"],
        },
        buttonTheme: [
            {
              class: "hg-submit",
              buttons: "{enter}",
            },
        ],
    });
    document.querySelector("#memnumform input[name='membership_num']").addEventListener("input", event => {
        keyboard_memnum.setInput(event.target.value);
    });

    // Start with Reset
    resetPage();
};


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


/* ========== Cheat Codes ========== */
const runCommand = (cmd) => {
    console.log("Running Command:", cmd);
    switch (cmd.toUpperCase()) {
        case 'HOME': // Navigate to root path
            window.location.href = '/';
            break;
        default:
            break;
    }
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
    err_lastActiveElement = undefined;

    // Body Text
    $('span.first_name').text('');
    $('span.last_name').text('');
    $('span.status_name span').text('');
    $('span.status_name span').attr("class", ""); // clear classes
    $('span.event_name').text('');

    /* Clear Form Data */
    // Event Selection
    $('#eventform input[type=radio]').prop('checked', false);
    // Scan
    $('#scanform input[type=text]').val('');
    // Guest
    $('#guestform input[type=text]').val('');
    document.querySelectorAll("#guestform input").forEach(input => {
        keyboard_guest.setInput(input.value, input.id);
    });
    // Membership Number
    $('#memnumform input[type=text]').val('');
    keyboard_memnum.setInput('');

    // Save error message
    $('span.error_msg').text('');
    // Attendance hidden form (in "saving" state)
    $('#attendanceform input[name=contact_pk]').val('');
    $('#attendanceform input[name=event_pk]').val('');

    /* Move to top */
    if (g_events.length == 1) {
        // only 1 event, automatically select it & submit
        $('#eventform input[type=radio]').prop('checked', true);
        submitEvent();
    } else {
        jumpTo("events"); // user to select event
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
    $('span.status_name span').text(member['status']);
    $('span.status_name span').addClass(member['status']);
    // Set Member for attendance record
    $('#attendanceform input[name=contact_pk]').val(member['contact_id']);

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
    // Scan Text
    var qrtext = $('#scanform input[name=contact_id]').val();

    // Run Command (?)
    cmdResult = /\{CMD\}\{(.*)\}/.exec(qrtext);
    if (cmdResult) {
        runCommand(cmdResult[1]);
        return false;
    }

    // Get Member
    const member_obj = await getMember.byContactID(qrtext);

    if (!member_obj) {
        $('#scanform input[type=text]').val(''); // clear form so new scan can follow it
        errorSet("Member with contact_id '" + qrtext + "' could not be found", "Unknown");
    } else {
        continueWithMember(member_obj);
    }
}

/* ----- Membership Number ----- */
const submitMemberNumber = async () => {
    // Get member (by their membership number)
    var membership_num = $('#memnumform input[name=membership_num]').val();
    const member_obj = await getMember.byMemberNum(membership_num);

    if (!member_obj) {
        errorSet(
            "Member with number '" + membership_num + "' could not be found", "Not Found"
        );
    } else {
        continueWithMember(member_obj);
    }
}

/* ----- Guest ----- */
const submitGuest = async () => {
    // Guest Data
    contact_data = {
        "csrfmiddlewaretoken": $('#guestform input[name=csrfmiddlewaretoken]').val(),
        "first_name": $('#guestform input[name=first_name]').val(),
        "last_name": $('#guestform input[name=last_name]').val(),
        "email_address": $('#guestform input[name=email]').val(),
        //"mobile_number": $('#guestform input[name=mobile]').val(),
    }
    console.log(contact_data);

    jumpTo("saving");

    // Create Contact
    var response = $.post(
        "/api/contact/",
        contact_data,
        (data) => {
            console.log(data);
        }
    ).then(
        (value) => { // success
            console.log(value);
            // Set guest values
            $('span.first_name').text(value['first_name']);
            $('span.last_name').text(value['last_name']);
            $('span.status_name span').text('GUEST');
            $('span.status_name span').addClass('GUEST');

            // Remember contact id for attendance
            $('#attendanceform input[name=contact_pk]').val(value['pk'])

            // Save
            saveAttendance.fromForm();
        },
        (reason) => { // failure
            console.error(reason);
            jumpTo("signin_guest");
            errorSet(reason.responseText);
        }
    );

}

/* ----- Record Attendance ----- */
const saveAttendance = (contact_pk, event_pk) => {
    // Submit Attendance to REST API
    attendance_obj = {
        "csrfmiddlewaretoken": $('#attendanceform input[name=csrfmiddlewaretoken]').val(),
        "contact": contact_pk,
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
            console.error(reason);
            errorSet(reason.responseText);
        }
    );
}

saveAttendance.fromForm = () => {
    saveAttendance(
        $('#attendanceform input[name=contact_pk]').val(),
        $('#attendanceform input[name=event_pk]').val()
    );
}

/* ----- Error Handling ----- */
const errorReset = () => {
    // Re-focus element (if applicable)
    if (err_lastActiveElement) {
        err_lastActiveElement.focus();
    }
    err_lastActiveElement = undefined;

    $('.error-dialog').hide();
}

errorReset.in = (timeout_ms) => {
    setTimeout(() => {
        errorReset();
    }, timeout_ms);
}


const errorSet = (message, title) => {
    // Title
    if (title === undefined) {
        title = 'Error';
    }
    $('.error-dialog .error-title').text(title);

    // Message
    $('.error-dialog .error-message').text(message);

    // Remove focus from active elemnt (if applicable)
    err_lastActiveElement = document.activeElement;
    if (err_lastActiveElement) {
        err_lastActiveElement.blur();
    }

    // Play Sound & Display
    playSound('sound_error');
    $('.error-dialog').show();
}
