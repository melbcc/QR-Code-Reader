# Django Web Application

## Setup

First start the [database service](../database)

```bash
# Install required libraries
python -m pip install --upgrade pip
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

All `get` and `create` REST API actions sent to CiviCRM need to be
authenticated. This protects the data from being read or changed from an
anonymous source.

**Create `service.xxx` user**

Each scanner should have a different user to access the CiviCRM database.\
(Follow these instructions)[../doc/NewUserScanner.md] to do so, and
remember the user's API key.

In the event one of the scanners is stolen, that user account can be can
be cancelled without effecting any of the other scanners at other locations.

**Create `~/civicrm-keys.json`**

Once a `scanner.<location>` user exists...

```bash
touch ~/civicrm-keys.json
chmod 644 ~/civicrm-keys.json
```

Edit the contents of `~/civicrm-keys.json` to be:

```json
{
    "site_key": "acbd18db4cc2f85cedef654fccc4a4d8",
    "user_key": "fdba98970961edb2"
}
```

Note: the above keys are made up, so replace them with actual keys

**Run Script**

If everything is setup and authenticated correctly, the following
script should run and download all relevant CiviCRM data.

```bash
./manage.py import_civicrm
```

## Admin Access

navigate to http://localhost:8000/admin and login with
* username: admin
* password: admin
