from django.db import models
from django.utils import timezone


class Member(models.Model):
    # Personal Data
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20)

    # Membership & Status
    contact_id = models.CharField(max_length=20)
    membership_num = models.CharField(max_length=20)
    end_date = models.DateTimeField('membership end', null=True, blank=True)

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

    def __str__(self):
        return "{first_name} {last_name} [{membership_num}]".format(
            first_name=self.first_name,
            last_name=self.last_name,
            membership_num=self.membership_num,
        )


class Location(models.Model):
    name = models.CharField(max_length=200, blank=True)
    remote_key = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Event(models.Model):
    remote_key = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
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


class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    checkin_time = models.DateTimeField('checkin time', null=True, blank=True)
