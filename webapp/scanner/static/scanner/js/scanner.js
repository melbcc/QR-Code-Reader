const getMember = async (membership_num) => {
    // Clean up ID
    // be tollerant of noise (like that from the QR code)
    memberid = membership_num.match(/\d*$/)[0];

    // Query REST
    const response = await fetch('/api/members/' + memberid + '/');
    var member = await response.json(); //extract JSON from the http response
    if (response.status != 200) {
        member = null;
    }
    return member;
}

const queryQRCode = async () => {
    /* Get member */
    var qrtext = $('#scanform input[name=memberid]').val();
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
