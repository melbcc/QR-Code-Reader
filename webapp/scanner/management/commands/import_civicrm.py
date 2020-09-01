import os
import requests
import re
import argparse
from datetime import datetime
import pytz
import json
from itertools import chain

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

import scanner.models


class Command(BaseCommand):
    help = "Import members from CiviCRM"

    REST_URL_BASE = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'

    def add_arguments(self, parser):

        def t_model(value):
            if value not in scanner.models.civicrm_tables:
                raise argparse.ArgumentTypeError("invalid table: {!r}".format(value))
            return scanner.models.civicrm_tables[value]

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
            help="site key (default from 'CIVICRM_SITEKEY' env var)",
        )
        group.add_argument(
            '--user-key', dest='user_key',
            help="user key (default from 'CIVICRM_USERKEY' env var)",
        )

        parser.add_argument(
            'models', metavar='TABLE', type=t_model, nargs='*',
            help='Table to import, if none are given, all are imported, options include: {}'.format(
                ', '.join([k for (k, v) in sorted(scanner.models.civicrm_tables.items(), key=lambda x: x[1].import_order)])
            ),
        )

    def civicrm_get(self, table_name, *fields, **conditions):
        print_ok = conditions.pop('print_ok', True)

        # Generate Payload
        payload = {
            'entity': table_name,
            'action': 'get',
            'api_key': self.api_key,
            'key': self.key,
            'json': 1,
            'options[limit]': 0,
            'return': ','.join(fields),
            'sequential': 1,
        }
        # TODO: can't get qualifier
        payload.update({
            k: json.dumps(v, separators=(',', ':'))
            for (k, v) in conditions.items()
        })

        # Send Request
        request = requests.post(self.REST_URL_BASE, data=payload)

        if request.status_code != 200:
            raise ValueError("response status code: {!r}".format(request.status_code))

        # Extract Data
        request_json = request.json()
        if request_json['is_error']:
            raise ValueError("response error message: {!r}".format(request_json.get('error_message', None)))

        if print_ok:
            self.stdout.write('    ' + self.style.SUCCESS('[ok]') + " received data for {} {}(s)".format(
                request_json['count'], table_name,
            ))
        return request_json

    def import_model(self, cls):
        """
        Import model data from remote database
        """
        self.stdout.write('  Fetching data from CiviCRM ...')

        remote_fieldmap = getattr(cls, 'remote_fieldmap', {})
        remote_conditions = {}

        import_limiter_data = getattr(cls, 'import_limiter_data', None)
        if import_limiter_data:
            # Get limiter information (from remote DB)
            remote_data = self.civicrm_get(
                import_limiter_data['model'],
                import_limiter_data['field'],
            )
            remote_conditions = {
                'id': {
                    'IN': list(map(
                        lambda o: int(o.get(import_limiter_data['field'])),
                        remote_data['values']
                    )),
                },
            }

        # Sending Request(s)
        #   NOTE: could never get REST request id={"IN":[1,2,3]} (or similar)
        #         requests working, so it's done manually in a loop
        remote_values = {}
        if not remote_conditions:  # nothing special
            remote_values = self.civicrm_get(
                cls.__name__,
                'id', *remote_fieldmap.keys(),
            )['values']
        elif isinstance(remote_conditions.get('id', {}).get('IN', None), list):
            # manually implement id={"IN":[1,2,3]} fetaure
            remote_values = list(chain(*(
                self.civicrm_get(cls.__name__, 'id', *remote_fieldmap.keys(), id=i)['values']
                for i in remote_conditions['id']['IN']
            )))
        else:
            raise RuntimeError("oops! should never get here")

        # Import Loop
        self.stdout.write('  Writing to local database ...')
        count = {'created': 0, 'updated': 0}
        for data in remote_values:
            if self.showdata:
                self.stdout.write('{!r}'.format(data))
            try:
                (event, created) = cls.objects.update_or_create(
                    remote_key=data['id'],
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
            '    ' + self.style.SUCCESS('[ok]') + ' ' +
            '{model_name} imported (added {created}, updated {updated})'.format(
                model_name=cls.__name__,
                **count
            )
        )

    def clean_deleted_model(self, cls):
        """
        Remove local model instances that no longer exist on the remote.

        Method: Send REST request per model instance, read response and
        act accordingly.
        """
        func = getattr(cls, 'remote_cleanup_queryset', None)
        if func is None:
            return

        queryset = func()
        self.stdout.write('  Cleaning {} objects ...'.format(queryset.count()))

        for obj in queryset:
            # Request Remote Object
            remote_data = self.civicrm_get(
                cls.__name__,
                'id',
                id=int(obj.remote_key),
                print_ok=False,  # be silent
            )

            # Remove if no results returned
            if remote_data['count'] > 0:
                self.stdout.write('    {!r} {}'.format(obj, self.style.SUCCESS('[ok]')))
            else:
                # Delete object
                self.stdout.write('    {!r} {}'.format(obj, self.style.ERROR('[removed]')))
                obj.delete()
                self.stdout.write('      removed {!r} from local database'.format(obj))

    def handle(self, *args, **kwargs):
        self.showdata = kwargs['showdata']

        # ----- Get Keys
        self.api_key = kwargs.get('user_key', None) or os.environ.get('CIVICRM_USERKEY', None)
        self.key = kwargs.get('site_key', None) or os.environ.get('CIVICRM_SITEKEY', None)
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
                    self.stdout.write(self.style.NOTICE(model.__name__))
                    self.import_model(model)
                    self.clean_deleted_model(model)
            except Exception as e:
                if self.strict:
                    raise
                self.stdout.write(
                    self.style.ERROR('[{}]'.format(e.__class__.__name__)) +
                    ' {!r}'.format(e.args)
                )
