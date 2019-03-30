# MelbPC QR-Code Scanner Setup

This page has a complete yet consice list of instructions to setup a new
scanner from with new hardware.

## Operating System - Raspbian

Download and install _Rasbian_ onto the hardware:

* Download `Raspbian Stretch with desktop` from the [download page](https://www.raspberrypi.org/downloads/raspbian/)
* Install onto Raspberry Pi - [Installation guide](https://www.raspberrypi.org/documentation/installation/installing-images/README.md)

The remainder of this installation will assume you're using the standard
`pi` user.

**Option: use `dd` from Linux**

If you're using a Linux pc to:

```
image_name=2018-11-13-raspbian-stretch.img
device=/dev/sdX
dd bs=4M if=${image_name} of=${device} conv=fsync
```

**Booting Raspberry Pi**

When booting for the first time, follow the on-screen prompts to configure:

* Locale
* `pi` user password (remember it)
* WiFi
* (and more?)

## Clone this Repository

On the raspberry pi:

```
cd ~
git clone https://github.com/carryonrewardless/QR-Code-Reader.git
```

This will clone the repository to `/home/pi/QR-Code-Reader` and set
the branch to `master` (default).

## Apps, Libs, and Configure

**Enable `SSH`**\
(follow [this link](https://www.raspberrypi.org/documentation/remote-access/ssh/) and read the "Enable SSH" section)

From the project root directory:

```
# Update all currently installed software
sudo apt update
sudo apt upgrade

# Screen
sudo apt install screen

# Docker
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo groupadd docker
sudo gpasswd -a pi docker

# Python 3.x
sudo apt install python3 python3-pip

# PosgreSQL Database Client
sudo apt install libpq-dev postgresql postgresql-contrib

# Browser
sudo apt install chromium-browser
```

**Reboot & Test Docker**

Reboot the Raspberry Pi, then:

```
docker run hello-world
```

You should see a `Hello from Docker!` message mixed in with almost a screen
of text; positive messages will indicate it's working ;).

**Set `python3` as default**

* assumption: `/usr/bin/python` is a symlink
* assumption: `python3 --version` == `Python 3.5.2`

(adjust accordingly)

```
cd /usr/bin
sudo rm python
sudo ln -s python3.5 python
```

**Install python libraries**

```
cd ~/QR-Code-Reader
sudo python -m pip install --upgrade pip
sudo python -m pip install -r webapp/requirements.txt
```

**Window-Manager Settings**

* Turn off screensaver (perhaps dim backlight instead?)


## Initialize Local Database

**Start Database service (manually)**

In a terminal run:

```
~/QR-Code-Reader/database/run.sh
```

In another terminal run:

```
cd ~/QR-Code-Reader/webapp

# Initialize Database
./manage.py migrate

# Create Admin User (in Django)
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@nowhere.com', 'admin')" | python manage.py shell
```

**Add CiviCRM Keys**

Follow instructions in [webapp](webapp/README.md) to create a
`~/civicrm-keys.json` file.

```
cd ~/QR-Code-Reader/webapp
python manage.py import_civicrm
```


## `/etc/rc.local`

Add the following to the `/etc/rc.local` file, before the `exit 0` line:

```
#!/bin/sh

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

# Start Services
sudo -iu pi /usr/bin/screen -dmS database bash -c /home/pi/QR-Code-Reader/database/run.sh
sudo -iu pi /usr/bin/screen -dmS webapp bash -c /home/pi/QR-Code-Reader/webapp/runserver.sh

# Wait for postgres database to spin up
sleep 10s

# Import updates to CiviCRM
orig_dir=${PWD}
cd /home/pi/QR-Code-Reader/webapp
python manage.py import_civicrm --keyfile /home/pi/civicrm-keys.json
cd $orig_dir

exit 0
```

**Reboot**

Reboot the Raspberry Pi, that should start the above services

To verify this, you can run `screen -list`. That should show 2 sessions running,
called `database` and `webapp`.

**Need to Debug?**

To read the log output of those services, you can "attach" to a `screen`
session with:

for `screen_name` = `database` or `webapp`

```
screen -r $screen_name
# press Ctrl+A, D to detatch from screen session
```

## `~/.config/lxsession/LXDE-pi/autostart`

```
mkdir -p ~/.config/lxsession/LXDE-pi
```

Create a `~/.config/lxsession/LXDE-pi/autostart` file with the contents:

```
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@chromium-browser --start-fullscreen -a file:///home/pi/QR-Code-Reader/startup.html
```

## `/etc/sudoers`

```
sudo visudo
```

Add to `/etc/sudoers`

```
pi ALL=(ALL) NOPASSWD: /sbin/poweroff
pi ALL=(ALL) NOPASSWD: /sbin/reboot
```

This will enable the `pi` user to turn off, and reboot the raspberry
pi by command-line without the need to enter a password.

## CRON

Edit the `pi` user's crontab with `crontab -e` (more detailed instructions
can be found [here](https://www.raspberrypi.org/documentation/linux/usage/cron.md))

```
0 0 * * *  cd /home/pi/QR-Code-Reader/webapp && python manage.py import_civicrm
*/5 * * * *  cd /home/pi/QR-Code-Reader/webapp && python manage.py export_attendance
```

## Scanner Command(s)

When the scanner is set up, there is no touch-friendly way to navigate
away from the membership scanning cycle.

Instead, you can scan a "command" QR-code, such as those below.

It's recommended you print these and keep near the scanner so they may
be used by the individual hosting the event.

### `{CMD}{HOME}`

![CMD HOME](HOME.png)
