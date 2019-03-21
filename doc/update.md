# MelbPC QR-Code Scanner Update

This is how to update an existing installation of the scanner with any
updates from this repository.

Note: this is not an infalible method by any means, so if you get stuck,
then you can always format the raspberry pi and re-install from the
[setup instruction](setup.md).

The following methods are set

## Pull contents

Pull the latest contents from github

```
git pull origin master
```

## Django migration

```
cd webapp
python -m pip install
./manage.py migrate
```

If this works, then you're all set! your web application should be running
and up to date.

If the above command worked (ie: no error) but you're not seeing the updates,
try rebooting the raspberry pi.

If it didn't work, try the next step.


## Clean Database

```
pushd database
./wipe-data.sh
popd

pushd webapp
./manage.py migrate
popd
```

If *that* worked, then you'll also need to re-add the admin django user, and
refresh the database.

```
cd webapp

# Add admin user
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@nowhere.com', 'admin')" | python manage.py shell
# Re-import CiviCRM data
./manage.py import_civicrm
```

and *now* you're good to go


## Last Resort
