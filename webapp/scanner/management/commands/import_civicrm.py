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
    help = "Import members from CiviCRM"

    REST_URL_BASE = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'
    DEFAULT_KEYFILE = '{HOME}/civicrm-keys.json' if 'HOME' in os.environ else 'civicrm-keys.json'

    def add_arguments(self, parser):

        def t_model(value):
            if value not in scanner.models.civicrm_tables:
                raise argparse.ArgumentTypeError("invalid table: {!r}".format(value))
            return scanner.models.civicrm_tables[value]

        def t_env_formatted_str(value):
            return value.format(**os.environ)

        parser.add_argument(
            '--showdata', dest='showdata',
            default=False, const=True, action='store_const',
            help="Prints downloaded data.",
        )
        parser.add_argument(
            '--strict', default=False, const=True, action='store_const',
            help="if set, the first failure will stop the script",
        )

        group = parser.add_argument_group('CiviCRM Options')
        group.add_argument(
            '--site-key', dest='site_key',
            help="CiviCRM site key (default from keyfile)",
        )
        group.add_argument(
            '--user-key', dest='user_key',
            help="CiviCRM user key (default from keyfile)",
        )

        default_keyfile = t_env_formatted_str(self.DEFAULT_KEYFILE)
        group.add_argument(
            '--keyfile', dest='keyfile',
            default=default_keyfile, type=t_env_formatted_str,
            help="CiviCRM key json file (default: {!r})".format(default_keyfile),
        )

        parser.add_argument(
            'models', metavar='TABLE', type=t_model, nargs='*',
            help='Table to import, if none are given, all are imported, options include: {}'.format(
                ', '.join([k for (k, v) in sorted(scanner.models.civicrm_tables.items(), key=lambda x: x[1].import_order)])
            ),
        )

    def get_keys(self, filename):
        if not os.path.exists(filename):
            return {}
        return json.load(open(filename, 'r'))

    def import_model(self, cls):
        self.stdout.write(self.style.NOTICE(cls.__name__))
        self.stdout.write('Fetching data from CiviCRM ...')

        remote_fieldmap = getattr(cls, 'remote_fieldmap', {})

        # Generate Payload
        payload = {
            'entity': cls.__name__,
            'action': 'get',
            'api_key': self.api_key,
            'key': self.key,
            'json': 1,
            'options[limit]': 0,
            'return': ','.join(['id'] + list(remote_fieldmap.keys())),
        }

        # Send Request
        request = requests.post(self.REST_URL_BASE, data=payload)
        if request.status_code != 200:
            raise ValueError("response status code: {!r}".format(request.status_code))

        # Extract Data
        request_json = request.json()
        if request_json['is_error']:
            raise ValueError("response error message: {!r}".format(request_json.get('error_message', None)))

        self.stdout.write('   ' + self.style.SUCCESS('[ok]') + ' received data for {} objects'.format(request_json['count']))

        # Import Loop
        self.stdout.write('Writing to local database ...')
        count = {'created': 0, 'updated': 0}
        for (remote_id, data) in request_json['values'].items():
            if self.showdata:
                self.stdout.write('{!r}'.format(data))
            try:
                (event, created) = cls.objects.update_or_create(
                    remote_key=remote_id,
                    defaults={
                        lkey: f(data.get(rkey, None))
                        for (rkey, (lkey, f)) in remote_fieldmap.items()
                    }
                )
                count['created' if created else 'updated'] += 1

            except IntegrityError:
                pass  # don't store model, just ignore it
            except Exception as e:
                if self.strict:
                    raise
                self.stdout.write(
                    self.style.ERROR('[{}]'.format(e.__class__.__name__)) +
                    ' {!r}'.format(e.args)
                )

        self.stdout.write(
            '   ' + self.style.SUCCESS('[ok]') + ' ' +
            '{model_name} imported (added {created}, updated {updated})'.format(
                model_name=cls.__name__,
                **count
            )
        )

    def handle(self, *args, **kwargs):
        self.showdata = kwargs['showdata']

        # ----- Get Keys
        key_data = self.get_keys(kwargs['keyfile'])
        self.api_key = kwargs.get('user_key', None) or key_data.get('user_key', None)
        self.key = kwargs.get('site_key', None) or key_data.get('site_key', None)
        self.strict = kwargs['strict']

        # Validate
        if None in (self.api_key, self.key):
            raise CommandError("Authentication keys not set")

        # ----- Import Models
        # note: this design ensure models are always imported in the correct
        #       order (where possible)
        for model in sorted(scanner.models.civicrm_tables.values(), key=lambda x: x.import_order):
            try:
                if (model in kwargs['models']) or (not kwargs['models']):
                    self.import_model(model)
            except Exception as e:
                if self.strict:
                    raise
                self.stdout.write(
                    self.style.ERROR('[{}]'.format(e.__class__.__name__)) +
                    ' {!r}'.format(e.args)
                )
