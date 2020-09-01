# Development Setup

## Pre-requisites

Assuming you're running on a debian-based OS (like Ubuntu):

```bash
sudo apt install docker-compose
```

## First Startup

Create a file ``.env.civicrm`` in the project's root directory with the
following content (with keys replaced with real ones):

```
CIVICRM_SITEKEY=acbd18db4cc2f85cedef654fccc4a4d8
CIVICRM_USERKEY=fdba98970961edb2
```

Build, and start docker services:

```bash
docker-compose up -d
./manage.sh migrate
./manage.sh create_admin_user admin admin
./manage.sh import_civicrm
```

You should now be able to see web-services:

* http://localhost:8000/admin - login with admin:admin
* http://localhost:8000/api - for REST api stuff
* http://localhost:8000 - scanner service
