# MelbPC QR-Code Scanner Setup

## Operating System - Raspbian

## Apps, Libs, and Configure

From the project root directory:

```
sudo apt update
sudo apt install docker-ce-cli
sudo apt install python3 python3-pip
python3 -m pip install --upgrade pip
python3 -m pip install -r webapp/requirements.txt
```

**Configure Django**

```
cd webapp

# Initialize Database
./manage.py migrate

# Create Admin User (in Django)
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@nowhere.com', 'admin')" | python3 manage.py shell
```

**Window-Manager Settings**

* Turn off screensaver (perhaps dim backlight instead?)

## `/etc/rc.local`

**TODO:** add lines to run... are we sure these can't be services?

* `cd database ; ./run.sh`
* `cd webapp ; ./manage.py runserver`

## `~/.config/lxsession/LXDE-pi/autostart`

**TODO:** add lines to start:

* `chromium-browser --app=http://localhost:8000`

## `/etc/sudoers`

Add to `/etc/sudoers`

```
pi ALL= /sbin/poweroff
```

This will enable the `pi` user to turn off the raspberry pi by command.

## CRON

**TODO:** setup cron job for:

* `./manage.py import_civicrm` (every 24hrs)
* `./manage.py export_attendance` (every 5min)
