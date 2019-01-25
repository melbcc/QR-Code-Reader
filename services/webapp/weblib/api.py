from flask import jsonify
from models import Member

from .base import app


@app.route('/api/v1.0/member/<int:member_id>', methods=['GET'])
def get_tasks(member_id):
    from .base import session
    # Query database
    members = session.query(Member).filter_by(membership_num=str(member_id))

    # Validate result
    if members.count() == 0:
        abort(404)  # no entries found
    elif members.count() > 1:
        abort(500)  # more than one entry found (should not be possible)

    # Return the member found
    member = members.first()
    return jsonify(member.as_dict)

@app.route('/api/v1.0/coffeepot/request/<int:cup_count>', methods=['GET'])
def get_coffee(cup_count):
    if cup_count != 0:
        abort(418)  # RFC 7168 compliance
    return("Done!")
