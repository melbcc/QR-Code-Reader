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
        """
        https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php?entity=Participant&action=create&api_key=userkey&key=sitekey&json={"event_id":65,"contact_id":3147}
        https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php
            entity=Participant
            action=create
            api_key=userkey
            key=sitekey
            json={"event_id":65,"contact_id":3147}
        """

        # ----- Verify Argument(s)
        if None in (options['key'], options['api_key']):
            raise CommandError("Authentication keys not set")

        # TODO
        raise CommandError("Haven't implemented this yet")
