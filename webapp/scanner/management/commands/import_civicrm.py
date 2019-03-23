import os
import requests
import re
import argparse
from datetime import datetime
import pytz
import json

from django.core.management.base import BaseCommand, CommandError
from scanner.models import Membership, Event, Contact


class Command(BaseCommand):
    help = "Import members from CiviCRM"

    REST_URL_BASE = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'
    VALID_ACTIONS = [
        'contacts',
        'memberships',
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

    def import_contacts(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Contacts'))
        self.stdout.write('Fetching data from CiviCRM ...')
        params = [
            'entity=Contact',
            'action=get',
            'api_key={}'.format(kwargs['api_key']),
            'key={}'.format(kwargs['key']),
            'json=contact_id',
            'return={}'.format(','.join([
                'last_name',
                'first_name',
                #'postal_code',
                'custom_8',  # membership_num
            ])),
            'options[limit]=0',
        ]
        request = requests.get(self.REST_URL_BASE + '?' + '&'.join(params))
        raw_data = request.json()  # format: {'count': <int>, 'values': <members dict>, ... }
        self.stdout.write('   ' + self.style.SUCCESS('[ok]') + ' received data for {} contacts'.format(raw_data['count']))

        # Just return iterator for each member dict
        self.stdout.write('Writing to local database ...')
        count = {'created': 0, 'updated': 0}
        for contact_dict in raw_data['values'].values():
            (event, created) = Contact.objects.update_or_create(
                remote_key=contact_dict['id'],
                defaults={
                    'first_name': contact_dict['first_name'],
                    'last_name': contact_dict['last_name'],
                    'membership_num': contact_dict.get('custom_8', None),
                }
            )
            count['created' if created else 'updated'] += 1

        self.stdout.write(
            '   ' + self.style.SUCCESS('[ok]') + ' ' +
            'Contacts imported (added {created}, updated {updated})'.format(**count)
        )

    def import_memberships(self, *args, **kwargs):
        """Method to download and iterate through member data"""
        self.stdout.write(self.style.NOTICE('Memberships'))
        self.stdout.write('Fetching data from CiviCRM ...')
        params = [
            'entity=Membership',
            'action=get',
            'api_key={}'.format(kwargs['api_key']),
            'key={}'.format(kwargs['key']),
            'json=membership_id',
            'return={}'.format(','.join([
                'contact_id',
                'end_date',
                'status_id',
                'membership_type_id',
            ])),
            #'return=contact_id,last_name,first_name,postal_code,custom_8',
            #'api.Membership.get[custom_8,end_date,status_id.name]',
            'options[limit]=0',
        ]
        request = requests.get(self.REST_URL_BASE + '?' + '&'.join(params))
        raw_data = request.json()  # format: {'count': <int>, 'values': <members dict>, ... }
        self.stdout.write('   ' + self.style.SUCCESS('[ok]') + ' received data for {} memberships'.format(raw_data['count']))

        # Just return iterator for each member dict
        self.stdout.write('Writing to local database ...')
        count = {'created': 0, 'updated': 0}
        for member_dict in raw_data['values'].values():
            end_date = None
            if 'end_date' in member_dict:
                end_date = pytz.utc.localize(datetime.strptime(
                    member_dict['end_date'], '%Y-%m-%d' #'%Y-%m-%d %H:%M:%S'
                ))
            contact = Contact.objects.filter(remote_key=member_dict['contact_id']).first()

            # is membership type relevant?
            #   TODO: pull in MembershipType table, types 1 & 5
            #         are "Individual" and "Honorary" respectively.
            membership_relevant = False
            if member_dict['membership_type_id'] in ('1', '5'):
                membership_relevant = True

            if contact and membership_relevant:
                (member, created) = Membership.objects.update_or_create(
                    remote_key=member_dict['id'],
                    defaults={
                        'contact': contact,
                        'end_date': end_date,
                        'status_id': member_dict['status_id'],
                        'membership_type_id': member_dict['membership_type_id'],
                    }
                )
                count['created' if created else 'updated'] += 1

        self.stdout.write(
            '   ' + self.style.SUCCESS('[ok]') + ' ' +
            'Memberships imported (added {created}, updated {updated})'.format(**count)
        )

    def import_events(self, *args, **kwargs):
        """
        CiviCRM API URL sample::

            https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php?entity=Event&action=get&api_key=userkey&key=sitekey&json={"sequential":1,"return":"id,title,start_date,description,loc_block_id"}

        Working URL::

            https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php?entity=Event&action=get&api_key=userkey&key=sitekey&json=event_id&return=id,title,start_date,description,loc_block_id

        """
        self.stdout.write(self.style.NOTICE('Events'))
        self.stdout.write('Fetching data from CiviCRM ...')
        params = [
            'entity=Event',
            'action=get',
            'api_key={}'.format(kwargs['api_key']),
            'key={}'.format(kwargs['key']),
            'json=event_id',
            #'sequential=1',
            'return={}'.format(','.join([
                'id',
                'title',
                'start_date',
                #'description',
                'loc_block_id',
            ])),
            'options[limit]=0',
        ]
        request = requests.get(self.REST_URL_BASE + '?' + '&'.join(params))
        raw_data = request.json()
        self.stdout.write('   ' + self.style.SUCCESS('[ok]') + ' received data for {} events'.format(raw_data['count']))

        # Just return iterator for each member dict
        self.stdout.write('Writing to local database ...')
        count = {'created': 0, 'updated': 0}
        for event_dict in raw_data['values'].values():
            (event, created) = Event.objects.update_or_create(
                remote_key=event_dict['id'],
                defaults={
                    'title': event_dict['title'],
                    'start_time': pytz.utc.localize(datetime.strptime(
                        event_dict['start_date'], '%Y-%m-%d %H:%M:%S'
                    )),
                    #'location': event_dict['loc_block_id'],
                }
            )
            count['created' if created else 'updated'] += 1

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
