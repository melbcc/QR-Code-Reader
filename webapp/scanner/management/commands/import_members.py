import os
import requests

from django.core.management.base import BaseCommand, CommandError
from scanner.models import Member


class Command(BaseCommand):
    help = "Import members from CiviCRM"

    REST_URL_BASE = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'

    def add_arguments(self, parser):
        group = parser.add_argument_group('CiviCRM Options')
        group.add_argument(
            '--key', dest='key', default=os.environ.get('CIVICRM_KEY', None),
            help="key the first (default: environment variable CIVICRM_KEY)",
        )
        group.add_argument(
            '--apikey', dest='api_key', default=os.environ.get('CIVICRM_APIKEY', None),
            help="key the second (default: environment variable CIVICRM_APIKEY)",
        )

    def handle(self, *args, **options):
        # Verify
        if None in (options['key'], options['api_key']):
            raise CommandError("Authentication keys not set")

        def member_iter():
            """Method to download and iterate through member data"""
            params = [
                'entity=Contact',
                'action=get',
                'api_key={}'.format(options['api_key']),
                'key={}'.format(options['key']),
                'json=contact_id',
                'return=contact_id,last_name,first_name,postal_code,custom_8',
                'api.Membership.get[custom_8,end_date,status_id.name]',
                'options[limit]=0',
            ]
            request = requests.get(self.REST_URL_BASE + '?' + '&'.join(params))
            raw_data = request.json()  # format: {'count': <int>, 'values': <members dict>, ... }

            # Just return iterator for each member dict
            for member_dict in raw_data['values'].values():
                yield member_dict

        for member_dict in member_iter():
            # Nested fields
            exp_date = None
            status_id = None
            values = member_dict.get('api_Membership_get', {}).get('values', None)
            if values:
                exp_date = values[0].get('end_date', None)
                status_id = values[0].get('status_id', None)

            # TODO: write to local database
            member = Member(
                # Personal Data
                first_name=member_dict['first_name'],
                last_name=member_dict['last_name'],
                postal_code=member_dict['postal_code'],

                # Membership & Status
                membership_num=member_dict['custom_8'],
                end_date=exp_date,
                status_id=status_id,
            )
            member.save()

            #self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
