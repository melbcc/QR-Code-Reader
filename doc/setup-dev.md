# Development Setup

## Pre-requisites

Assuming you're running on a debian-based OS (like Ubuntu):

```bash
sudo apt install docker-compose
```

## First Startup

```
docker-compose up -d
./manage.sh create_admin_user admin admin
```

You should now be able to see web-services:

* https://localhost/admin - login with admin:admin
* https://localhost/api - for REST api stuff
* https://localhost/app/select - scanner service

*note* : the SSL cert for HTTPS is generated locally, so will not be verified... you'll most likely need to inform your browser to continue loading content from `localhost` regardless.

## Populating Data

The app *will* run with an empty database, but isn't very useful.

### Using dummy data (public)

Populate with a sanitised shortlist of events and members:

```bash
./manage.sh loaddata scanner/fixtures/test_data.json
```

*Hint:* To make events become "active", change some of their start/end times to be today, and now...

### Using real (MelbPC) CiviCRM Data

Create a file `civicrm.env` in the [`env`](env) directory with the
following content (with keys replaced with real ones):

```
CIVICRM_SITEKEY=acbd18db4cc2f85cedef654fccc4a4d8
CIVICRM_USERKEY=fdba98970961edb2
```

Import using django admin script:

```bash
./manage.sh import_civicrm
```

Note: you can also `export_attendance`, but only do this if you intend to keep track of the attendance records being tested, then delete them to leave production data unchanged.