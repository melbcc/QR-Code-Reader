import os
import requests

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q
from scanner.models import Contact, Attendance
from scanner.conf import settings


class Command(BaseCommand):
    help = "Export recorded attendance to CiviCRM"

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

    def create(self, table_name, **kwargs):
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
                raise ValueError("response status code: {!r}".format(request.status_code))

            self.stdout.write(self.style.ERROR(
                'Response status code: {}'.format(request.status_code)
            ))
            self.stdout.write('Content:')
            self.stdout.write(request.content.decode())
            return None

        request_json = request.json()
        if request_json['is_error']:
            if self.failfast:
                raise ValueError("response error  message: {!r}".format(request_json['error_message']))

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

        self.api_key = kwargs['api_key']
        self.key = kwargs['key']
        self.failfast = kwargs['failfast']

        # ----- Verify Argument(s)
        if None in (kwargs['key'], kwargs['api_key']):
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

        for attendance in attendance_queryset:
            (contact, event) = (attendance.contact, attendance.event)
            self.stdout.write('    {!r} : {!r}'.format(contact, event))
            participant = self.create('Participant',
                contact_id=contact.remote_key,
                event_id=event.remote_key,
            )
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
