from django.db import models
from django.utils import timezone

# ================================================
#          CiviCRM Mirrored Models
# ================================================
# All models with a 'remote_key' parameter are intended to be a partial
# mirror of the CiviCRM database.
# The 'remote_key' links the unique database entries on the remote system with
# the duplicate copied onto the RaspberryPi's local database.

class Contact(models.Model):
    remote_key = models.CharField(max_length=20)  # CiviCRM primary key
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    membership_num = models.CharField(max_length=20, blank=True, null=True)  # custom_8

    def __str__(self):
        return '{first_name} {last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name,
        )


class Membership(models.Model):
    remote_key = models.CharField(max_length=20)  # CiviCRM primary key
    end_date = models.DateTimeField('membership end', null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)

    STATUS_ID_CHOICES = {
        2: "CURRENT",
        3: "GRACE",
        4: "EXPIRED",
        5: "__blank5__",
        6: "__blank6__",
        7: "DECEASED",
    }
    status_id = models.IntegerField(
        choices=sorted(STATUS_ID_CHOICES.items(), key=lambda x: x[0]),
        null=True, blank=True,
    )

    @property
    def status(self):
        return self.STATUS_ID_CHOICES[self.status_id]

    @property
    def status_isok(self):
        return (self.status_id <= 3)

    @property
    def membership_num(self):
        return self.contact.membership_num

    @property
    def first_name(self):
        return self.contact.first_name

    @property
    def last_name(self):
        return self.contact.last_name

    def __str__(self):
        return "{contact} [{membership_num}]".format(
            contact=self.contact,
            membership_num=self.membership_num,
        )


class Location(models.Model):
    remote_key = models.CharField(max_length=20)
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    remote_key = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    start_time = models.DateTimeField('start time')

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        """True if event is a plausible candidate for a scanner"""
        delta = self.start_time - timezone.now()
        delta_hours = delta.total_seconds() / (60 * 60)
        return (-6 <= delta_hours <= 12)

    @property
    def start_time_epoch(self):
        return self.start_time.timestamp()


# ================================================
#          Local Only Models
# ================================================
# as opposed to those above that are mirrored from CiviCRM

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    checkin_time = models.DateTimeField('checkin time', null=True, blank=True)
