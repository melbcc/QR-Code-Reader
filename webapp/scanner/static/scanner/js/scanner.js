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

    // Send Query
    const response = await fetch('/api/members/' + contact_id + '/');

    // Return Member object or null
    var member = null;
    if (response.status == 200) {
        member = await response.json(); //extract JSON from the http response;
    }
    console.log(member);
    return member;
}


const getLocationList = async () => {
    // Lists all locations
    
}


const getEventList = async (location_id) => {

}


/* ========== Event Handlers ========== */
const queryQRCode = async () => {
    /* Get member */
    var qrtext = $('#scanform input[name=contact_id]').val();
    const member = await getMember(qrtext);

    if (member) {
          /* Inform user of status */
          $('#first_name').text(member['first_name']);
          $('#last_name').text(member['last_name']);
          $('#status_id').text(member['status_id']);
    } else {
          $('#first_name').text('error');
          $('#last_name').text('');
          $('#status_id').text('');
    }

    /* Fetch events */
    // TODO: pull relevant for this location
    //    select events that:
    //        are in 1 of the selected locations
    //        starts in <= 2hrs
    //        is currently in session, or
    //        ended <= 2hrs ago
    //    sorted by abs(start_time - current_time)

    /* Ask user which event */
    // TODO: if more than 1 event is available
    //    make visible a 2nd selection of the events.

    /* Give the "OK, og ahead" signal */
    // TODO: make OK overlay visible, and clear
}
