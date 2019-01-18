import os
import requests


def add_arguments(parser):
    """
    Adds arguments to an <argparse.ArgumentParser> instance
    """
    group = parser.add_argument_group('CiviCRM Options')
    group.add_argument(
        '--key', dest='key', default=os.environ.get('CIVICRM_KEY', None),
        help="key the first (default: environment variable CIVICRM_KEY)",
    )
    group.add_argument(
        '--apikey', dest='api_key', default=os.environ.get('CIVICRM_APIKEY', None),
        help="key the second (default: environment variable CIVICRM_APIKEY)",
    )


def fetch_member_data(api_key, key):
    uri = 'https://www.melbpc.org.au/wp-content/plugins/civicrm/civicrm/extern/rest.php'
    params = [
        'entity=Contact',
        'action=get',
        'api_key={}'.format(api_key),
        'key={}'.format(key),
        'json=contact_id',
        'return=contact_id,last_name,first_name,postal_code,custom_8',
        'api.Membership.get[custom_8,end_date,status_id.name]',
        'options[limit]=0',
    ]
    request = requests.get(uri + '?' + '&'.join(params))
    raw_data = request.json()  # format: {'count': <int>, 'values': <members dict>, ... }

    # Just return iterator for each member dict
    for member_dict in raw_data['values'].values():
        yield member_dict
