import os
import requests
import re
import argparse
from datetime import datetime
import pytz

from django.core.management.base import BaseCommand, CommandError
from scanner.models import Member


class Command(BaseCommand):
    help = "Import members from CiviCRM"

    REST_URL_BASE = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'
    VALID_ACTIONS = [
        'members',
        'locations',
        'events',
    ]

    def add_arguments(self, parser):

        def action_list(value):
            actions = set(re.split(r'\W+', value))

            # validate
            invalid_actions = actions - set(self.VALID_ACTIONS)
            if invalid_actions:
                raise argparse.ArgumentTypeError("invalid action(s): {!r}".format(invalid_actions))

            return actions

        group = parser.add_argument_group('CiviCRM Options')
        group.add_argument(
            '--key', dest='key', default=os.environ.get('CIVICRM_KEY', None),
            help="key the first (default: environment variable CIVICRM_KEY)",
        )
        group.add_argument(
            '--apikey', dest='api_key', default=os.environ.get('CIVICRM_APIKEY', None),
            help="key the second (default: environment variable CIVICRM_APIKEY)",
        )

        group = parser.add_argument_group('Actions')
        group.add_argument(
            '--actions', dest='actions', type=action_list, default=[],
            help="List of things to import: {!r}".format(self.VALID_ACTIONS),
        )

    def import_members(self, *args, **kwargs):
        """Method to download and iterate through member data"""
        self.stdout.write(self.style.NOTICE('Members'))
        self.stdout.write('Fetching data from CiviCRM ...')
        params = [
            'entity=Contact',
            'action=get',
            'api_key={}'.format(kwargs['api_key']),
            'key={}'.format(kwargs['key']),
            'json=contact_id',
            'return=contact_id,last_name,first_name,postal_code,custom_8',
            'api.Membership.get[custom_8,end_date,status_id.name]',
            'options[limit]=0',
        ]
        request = requests.get(self.REST_URL_BASE + '?' + '&'.join(params))
        raw_data = request.json()  # format: {'count': <int>, 'values': <members dict>, ... }
        self.stdout.write('   ' + self.style.SUCCESS('[ok]') + ' received data for {} members'.format(raw_data['count']))

        # Just return iterator for each member dict
        self.stdout.write('Writing to local database ...')
        count = {'created': 0, 'updated': 0}
        for member_dict in raw_data['values'].values():
            # Nested fields
            exp_date = None
            status_id = None
            contact_id = None
            values = member_dict.get('api_Membership_get', {}).get('values', None)
            if values:
                # contact_id
                contact_id = values[0].get('contact_id', None)
                # exp_date
                exp_date_str = values[0].get('end_date', None)
                if exp_date_str:
                    exp_date = pytz.utc.localize(datetime.strptime(
                        exp_date_str, '%Y-%m-%d' #'%Y-%m-%d %H:%M:%S'
                    ))
                # status_id
                status_id = values[0].get('status_id', None)

            # TODO: write to local database
            if contact_id:
                (member, created) = Member.objects.update_or_create(
                    contact_id=contact_id,
                    defaults={
                        # Personal Data
                        'first_name': member_dict['first_name'],
                        'last_name': member_dict['last_name'],
                        'postal_code': member_dict['postal_code'],

                        # Membership & Status
                        'membership_num': member_dict['custom_8'],
                        'end_date': exp_date,
                        'status_id': status_id,
                    }
                )
                count['created' if created else 'updated'] += 1

        self.stdout.write(
            '   ' + self.style.SUCCESS('[ok]') + ' ' +
            'Members imported (added {created}, updated {updated})'.format(**count)
        )

    def import_events(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Events'))
        count = {'created': 0, 'updated': 0}

        # TODO

        self.stdout.write(
            '   ' + self.style.SUCCESS('[ok]') + ' ' +
            'Events imported (added {created}, updated {updated})'.format(**count)
        )

    def import_locations(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Locations'))
        count = {'created': 0, 'updated': 0}

        # TODO

        self.stdout.write(
            '   ' + self.style.SUCCESS('[ok]') + ' ' +
            'Locations imported (added {created}, updated {updated})'.format(**count)
        )

    def handle(self, *args, **options):
        # ----- Verify Argument(s)
        if None in (options['key'], options['api_key']):
            raise CommandError("Authentication keys not set")

        # ----- Actions
        # Run all self.import_<action>() functions identified
        # by input parameters (or all if a white-list was not given)
        for action in self.VALID_ACTIONS:
            if (action in options['actions']) or (not options['actions']):
                getattr(self, 'import_' + action)(*args, **options)
