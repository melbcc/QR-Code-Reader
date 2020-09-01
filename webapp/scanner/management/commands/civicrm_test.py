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

    def add_arguments(self, parser):

        parser.add_argument(
            '--model', default='MembershipStatus',
            help="Model to import.",
        )

        group = parser.add_argument_group('CiviCRM Options')
        group.add_argument(
            '--site-key', dest='site_key',
            help="site key (default from 'CIVICRM_SITEKEY' env var)",
        )
        group.add_argument(
            '--user-key', dest='user_key',
            help="user key (default from 'CIVICRM_USERKEY' env var)",
        )

    def handle(self, *args, **kwargs):
        # ----- Get Keys
        self.api_key = kwargs.get('user_key', None) or os.environ.get('CIVICRM_USERKEY', None)
        self.key = kwargs.get('site_key', None) or os.environ.get('CIVICRM_SITEKEY', None)

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
