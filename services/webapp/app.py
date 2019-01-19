#!/usr/bin/env python

import os
import sys
import inspect
import re

import argparse
from flask import Flask, jsonify, abort, render_template, send_from_directory

# add ../lib folder
_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', '..', 'lib'))

from models import Member
from databases import local

# ----- Commandline Parameters
parser = argparse.ArgumentParser(description='Web Application.')

local.add_arguments(parser)

args = parser.parse_args()



# ----- Connect to Local Database
session = local.get_session(
	user=args.user,
	password=args.password,
	domain=args.domain,
	port=args.port,
	dbname=args.dbname,
)


# ----- Flask Application
app = Flask(__name__)

@app.route('/api/v1.0/member/<int:member_id>', methods=['GET'])
def get_tasks(member_id):
    # Query database
    members = session.query(Member).filter_by(membshipnum=str(member_id))

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

@app.route('/', methods=['GET'])
def render_root():
    return render_template('root.html')

@app.route('/scanner', methods=['GET'])
def render_scanner():
    return render_template('scanner.html')

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


app.run(debug=True)
