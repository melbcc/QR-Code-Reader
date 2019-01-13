#!/usr/bin/env python

import argparse
import requests
import os
import sys


# --------- Parse Arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument(
    '--key', dest='key', default=os.environ.get('CIVICRM_KEY', None),
    help="key the first (default: environment variable CIVICRM_KEY)",
)
parser.add_argument(
    '--apikey', dest='api_key', default=os.environ.get('CIVICRM_APIKEY', None),
    help="key the second (default: environment variable CIVICRM_APIKEY)",
)

args = parser.parse_args()

# --- Verify parameters
if None in (args.key, args.api_key):
    print("Authentication keys not set...")
    parser.print_help()
    sys.exit(1)

# ------ Fetch User Data
uri = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'
params = {
    'entity': 'Contact',
    'action': 'get',
    'api_key': args.api_key,
    'key': args.key,
    'json': 'contact_id',
    'return': 'contact_id:last_name:first_name:postal_code:custom_8',
    'api.Membership.get[custom_8:end_date:status_id.name]': None,
    'options[limit]': '0',
}
request = requests.get(uri, params=params)
data = request.json()

# ------ Upload to local db (?)
# TODO: what now?
print(data)
#__import__('ipdb').set_trace()

members = data['values']

for member in members.values():
	exp_date = None
	status_id = None
	values = member.get('api_Membership_get', {}).get('values', None)
	if values:
		exp_date = values[0].get('end_date', None)
		status_id = values[0].get('status_id', None)
	
	print((
		"Contact id: {contact_id} "
		"Name: {first_name} {last_name} "
		"Post Code: {postal_code} "
		"Membership No.: {custom_8} "
		"Expiry Date: {exp_date}"
		"Status ID: {status_id}"
	).format(
		exp_date=exp_date,
		status_id=status_id,
		**member
	))

