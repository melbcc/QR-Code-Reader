#!/usr/bin/env python

import argparse
import requests
import os
import sys


# --------- Parse Arguments
parser = argparse.ArgumentParser(description='Process some integers.')
group = parser.add_argument_group('CiviCRM Options')
group.add_argument(
    '--key', dest='key', default=os.environ.get('CIVICRM_KEY', None),
    help="key the first (default: environment variable CIVICRM_KEY)",
)
group.add_argument(
    '--apikey', dest='api_key', default=os.environ.get('CIVICRM_APIKEY', None),
    help="key the second (default: environment variable CIVICRM_APIKEY)",
)

#group = parser.add_argument_group('Local Database Options')

args = parser.parse_args()

# --- Verify parameters
if None in (args.key, args.api_key):
    print("Authentication keys not set...")
    parser.print_help()
    sys.exit(1)


# ------ Fetch User Data (from CiviCRM)
uri = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'
params = [
    'entity=Contact',
    'action=get',
    'api_key={}'.format(args.api_key),
    'key={}'.format(args.key),
    'json=contact_id',
    'return=contact_id,last_name,first_name,postal_code,custom_8',
    'api.Membership.get[custom_8,end_date,status_id.name]',
    'options[limit]=0',
]
request = requests.get(uri + '?' + '&'.join(params))
data = request.json()  # format: {'count': <int>, 'values': <members dict>, ... }


# ------ Upload to local db
for member in data['values'].values():
	# Nested fields
	exp_date = None
	status_id = None
	values = member.get('api_Membership_get', {}).get('values', None)
	if values:
		exp_date = values[0].get('end_date', None)
		status_id = values[0].get('status_id', None)

	# TODO: write to local database
	print((
		"Contact id: {contact_id} "
		"Name: {first_name} {last_name} "
		"Post Code: {postal_code} "
		"Membership No.: {custom_8} "
		"Expiry Date: {exp_date} "
		"Status ID: {status_id} "
	).format(
		exp_date=exp_date,
		status_id=status_id,
		**member
	))
