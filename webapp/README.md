# Django Web Application

## Setup

First start the [database service](../database)

```bash
python -m pip install -r requirements.txt

./manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@nowhere.com', 'admin')" | python manage.py shell

./manage.py runserver
```

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
./manage.py import_members
```

## Admin Access

navigate to http://localhost:8000/admin and login with
* username: admin
* password: admin
