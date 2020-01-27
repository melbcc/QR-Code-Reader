import os
import requests
import re
import argparse
from datetime import datetime
import pytz
import json

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

import scanner.models


class Command(BaseCommand):
    help = "Test CiviCRM API (only for debugging)"

    REST_URL_BASE = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'
    DEFAULT_KEYFILE = '{HOME}/civicrm-keys.json' if 'HOME' in os.environ else 'civicrm-keys.json'

    def add_arguments(self, parser):

        def t_env_formatted_str(value):
            return value.format(**os.environ)

        parser.add_argument(
            '--model',
            help="Model to import.",
        )

        default_keyfile = t_env_formatted_str(self.DEFAULT_KEYFILE)
        parser.add_argument(
            '--keyfile', dest='keyfile',
            default=default_keyfile, type=t_env_formatted_str,
            help="CiviCRM key json file (default: {!r})".format(default_keyfile),
        )

    def get_keys(self, filename):
        if not os.path.exists(filename):
            return {}
        return json.load(open(filename, 'r'))

    def handle(self, *args, **kwargs):
        # ----- Get Keys
        key_data = self.get_keys(kwargs['keyfile'])
        self.api_key = kwargs.get('user_key', None) or key_data.get('user_key', None)
        self.key = kwargs.get('site_key', None) or key_data.get('site_key', None)

        # Generate Payload
        payload = {
            'entity': kwargs['model'],
            'action': 'get',
            'api_key': self.api_key,
            'key': self.key,
            'json': 1,
            'options[limit]': 0,
            #'return': ','.join(['id'] + list(remote_fieldmap.keys())),
        }

        # Send Request
        request = requests.post(self.REST_URL_BASE, data=payload)
        if request.status_code != 200:
            raise ValueError("response status code: {!r}".format(request.status_code))

        # Extract Data
        request_json = request.json()

        print(json.dumps(request_json, indent=2))
