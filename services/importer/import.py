#!/usr/bin/env python

import argparse
import requests
import os
import sys
import inspect

# add ../lib folder
_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', '..', 'lib'))

from databases import civicrm, local
from models import Member


# --------- Parse Arguments
parser = argparse.ArgumentParser(description='Process some integers.')

civicrm.add_arguments(parser)
local.add_arguments(parser)

args = parser.parse_args()


# --- Verify parameters
if None in (args.key, args.api_key):
    print("Authentication keys not set...")
    parser.print_help()
    sys.exit(1)


# ------ Connect to Local Database
session = local.get_session(
	user=args.user,
	password=args.password,
	domain=args.domain,
	port=args.port,
	dbname=args.dbname,
)


# ------ Fetch User Data (from CiviCRM)
member_iter = civicrm.fetch_member_data(args.api_key, args.key)


# ------ Upload to Local Database
for member_dict in member_iter:
	# Nested fields
	exp_date = None
	status_id = None
	values = member_dict.get('api_Membership_get', {}).get('values', None)
	if values:
		exp_date = values[0].get('end_date', None)
		status_id = values[0].get('status_id', None)

	# TODO: write to local database
	member = Member(
	    id=member_dict['id'],
	    # Personal Data
	    first_name=member_dict['first_name'],
	    last_name=member_dict['last_name'],
	    postal_code=member_dict['postal_code'],

	    # Membership & Status
	    membshipnum=member_dict['custom_8'],
	    end_date=exp_date,
	    status_id=status_id,
	    #status_name=???,
	)
	session.add(member)
	session.commit()
