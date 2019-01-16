#!/usr/bin/env python

import argparse
import requests
import os
import sys
import inspect

# add ../lib folder
_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', '..', 'lib'))

from models import BaseModel, Member


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


# ------ Connect to Local Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
	'postgresql+psycopg2://{user}:{password}@{domain}/{db}?port={port}'.format(
		user='postgres',
		password='secret',
		domain='localhost',
		port=5432,
		db='mydb',
	),
	#pool_recycle=3600,
)

BaseModel.metadata.create_all(engine)  # creates tables if they don't already exist
BaseModel.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

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


# ------ Upload to Local Database

for member_dict in data['values'].values():
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
