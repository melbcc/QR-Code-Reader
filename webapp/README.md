# Django Web Application

## Setup

First start the [database service](../database)

```bash
# Install required libraries
python -m pip install -r requirements.txt

# Initialize Database
./manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@nowhere.com', 'admin')" | python manage.py shell

# Start local HTTP service
./manage.py runserver
```

That last command should give you a url you can use to see the scanner's
page (probably https://localhost:8000/)

_note_: if anything goes wrong with the database during setup (most likely
the `migrate` command), call `wipe-data.sh` in the [database](../database)
folder.

## Sample Data

Load sample data from fixtures with

```
./manage.py loaddata test_data
```

## Import from CiviCRM

**Add keys**

Create a file in this directory: `api_keys.sh`

```bash
#!/usr/bin/env bash
export CIVICRM_KEY=acbd18db4cc2f85cedef654fccc4a4d8
export CIVICRM_APIKEY=fdba98970961edb2
```

Note: the above keys are made up, so replace them with actual keys

**Run Script**

```bash
source api_keys.sh
./manage.py import_civicrm
```

## Admin Access

navigate to http://localhost:8000/admin and login with
* username: admin
* password: admin
