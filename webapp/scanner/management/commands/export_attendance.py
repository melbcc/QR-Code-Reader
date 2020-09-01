import os
import requests
import json

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q
from scanner.models import Contact, Attendance, ParticipantStatusType
from scanner.conf import settings


class CiviCRMRequestError(Exception):
    """Raised upon erroneous response from CiviCRM"""


class Command(BaseCommand):
    help = "Export recorded attendance to CiviCRM"

    REST_URL_BASE = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'

    def add_arguments(self, parser):

        group = parser.add_argument_group('CiviCRM Options')
        group.add_argument(
            '--site-key', dest='site_key',
            help="site key (default from 'CIVICRM_SITEKEY' env var)",
        )
        group.add_argument(
            '--user-key', dest='user_key',
            help="user key (default from 'CIVICRM_USERKEY' env var)",
        )

        group = parser.add_argument_group('Export Options')
        group.add_argument(
            '--ignore-guests', dest='create_guests',
            default=True, const=False, action='store_const',
            help="if set, Contacts are not created; guest attendance is ignored",
        )
        group.add_argument(
            '--no-purge', dest='purge',
            default=True, const=False, action='store_const',
            help="if set, don't remove old attendance records",
        )
        group.add_argument(
            '--fail-slow', dest='failfast',
            default=True, const=False, action='store_const',
            help="if set, tool continues after each failure (instead of exiting)",
        )
        group.add_argument(
            '--dryrun', dest='dryrun',
            default=False, const=True, action='store_const',
            help="if set, no create requests are sent to CiviCRM",
        )

    def get(self, table_name, **kwargs):
        payload = {
            'entity': table_name,
            'action': 'get',
            'api_key': self.api_key,
            'key': self.key,
            'json': 1,
            'return': 'id',
        }
        payload.update(kwargs)

        # Send Request
        request = requests.post(self.REST_URL_BASE, data=payload)
        if request.status_code != 200:
            raise CiviCRMRequestError("response status code: {!r}".format(request.status_code))

        # Extract Data
        request_json = request.json()
        if request_json.get('is_error', False):
            raise CiviCRMRequestError("response error message: {!r}".format(request_json.get('error_message', None)))

        # Return first
        if request_json['values']:
            for (remote_id, data) in request_json['values'].items():
                return data
        return {}

    def create(self, table_name, **kwargs):
        if self.dryrun:
            return None

        # Generate Payload
        payload = {
            'entity': table_name,
            'action': 'create',
            'api_key': self.api_key,
            'key': self.key,
            'json': 1,
        }
        payload.update(kwargs)

        # Send Request
        request = requests.post(self.REST_URL_BASE, data=payload)

        # Validate Response
        if request.status_code != 200:
            if self.failfast:
                raise CiviCRMRequestError("response status code: {!r}".format(request.status_code))

            self.stdout.write(self.style.ERROR(
                'Response status code: {}'.format(request.status_code)
            ))
            self.stdout.write('Content:')
            self.stdout.write(request.content.decode())
            return None

        request_json = request.json()
        if request_json['is_error']:
            if self.failfast:
                raise CiviCRMRequestError("response error  message: {!r}".format(request_json['error_message']))

            self.stdout.write(self.style.ERROR(
                'Error Message: {}'.format(request_json['error_message'])
            ))
            return None

        # Return data
        return request_json

    def handle(self, *args, **kwargs):
        """
        https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php?entity=Participant&action=create&api_key=userkey&key=sitekey&json={"event_id":65,"contact_id":3147}
        https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php
            entity=Participant
            action=create
            api_key=userkey
            key=sitekey
            json={"event_id":65,"contact_id":3147}
        """

        self.failfast = kwargs['failfast']
        self.dryrun = kwargs['dryrun']

        # ----- Get Keys
        self.api_key = kwargs.get('user_key', None) or os.environ.get('CIVICRM_USERKEY', None)
        self.key = kwargs.get('site_key', None) or os.environ.get('CIVICRM_SITEKEY', None)

        # Validate
        if None in (self.api_key, self.key):
            raise CommandError("Authentication keys not set")

        # ----- Create Guest Contacts
        if kwargs['create_guests']:
            self.stdout.write(self.style.NOTICE('Create guest Contacts --> CiviCRM Contact objects'))
            # Identify guests
            guest_attendance = Attendance.objects.filter(
                Q(contact__remote_key__isnull=True) | Q(contact__remote_key__exact=''),  # contact signed in as a guest
                export_time=None,  # not yet exported
            ).prefetch_related('contact')


            # Create each guest as a Contact on CiviCRM
            for attendance in guest_attendance:
                contact = attendance.contact
                self.stdout.write('    {}'.format(contact))

                # Export new Contact
                self.stdout.write('        Exporting: {!r} ...'.format(contact))
                r_contact = self.create('Contact',
                    contact_type='Individual',
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                )
                if not r_contact:
                    continue

                # Save remote key
                contact.remote_key = '{}'.format(r_contact['id'])
                contact.save()

                # Export email address
                if contact.email_address:
                    self.stdout.write('        Exporting Email: {!r} ...'.format(contact.email_address))
                    email = self.create('Email',
                        contact_id=contact.remote_key,
                        email=contact.email_address,
                    )

                # Export mobile number
                if contact.mobile_number:
                    self.stdout.write('        Exporting Mobile: {} ...'.format(contact.mobile_number))
                    phone = self.create('Phone',
                        contact_id=contact.remote_key,
                        phone=str(contact.mobile_number),
                    )

        # Get & Export attendance list
        self.stdout.write(self.style.NOTICE('Export local Attendance --> CiviCRM Participation objects'))
        attendance_queryset = Attendance.objects.filter(
            Q(contact__remote_key__isnull=False) & ~Q(contact__remote_key__exact=''),
            export_time=None,
        ).prefetch_related('contact', 'event')
        status_attended = ParticipantStatusType.objects.get(name='Attended')

        for attendance in attendance_queryset:
            (contact, event) = (attendance.contact, attendance.event)
            self.stdout.write('    {!r} : {!r}'.format(contact, event))

            params = {
                'contact_id': contact.remote_key,
                'event_id': event.remote_key,
            }

            # Find existing CiviCRM entry
            participant = self.get('Participant', **params)
            if participant:
                params.update({
                    'id': participant['id'],
                })

            # Create new / update existing CiviCRM entry
            params.update({
                'register_date': attendance.checkin_time,
                'participant_status_id': status_attended.remote_key,
            })
            participant = self.create('Participant', **params)
            if participant:
                attendance.export_time = timezone.now()
                attendance.save()

        if kwargs['purge']:
            self.stdout.write(self.style.NOTICE('Purge local Attendance records'))
            # Remove all attendance records exported > ATTENDANCE_PURGE_TIMEOUT ago
            purge_queryset = Attendance.objects.filter(
                export_time__lt=(timezone.now() - timezone.timedelta(
                    seconds=settings.SCANNER_ATTENDANCE_PURGE_TIMEOUT
                )),
            )
            self.stdout.write('    Deleting {} Attendance objects'.format(purge_queryset.count()))
            purge_queryset.delete()
