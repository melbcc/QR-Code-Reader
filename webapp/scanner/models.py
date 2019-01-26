from django.db import models


class Member(models.Model):
    # Personal Data
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20)

    # Membership & Status
    contact_id = models.CharField(max_length=20)
    membership_num = models.CharField(max_length=20)
    end_date = models.DateTimeField('membership end', null=True, blank=True)

    STATUS_ID_CHOICES = (
        (2, "CURRENT"),
        (3, "GRACE"),
        (4, "EXPIRED"),
        (5, "__blank5__"),
        (6, "__blank6__"),
        (7, "DECEASED"),
    )
    status_id = models.IntegerField(
        choices=STATUS_ID_CHOICES,
        null=True, blank=True,
    )

    def __repr__(self):
        return "<{cls}: {first_name} {last_name} [{membership_num}]>".format(
            cls=type(self).__name__,
            first_name=self.first_name,
            last_name=self.last_name,
            membership_num=self.membership_num,
        )

class Location(models.Model):
    name = models.CharField(max_length=200, blank=True)
    remote_key = models.CharField(max_length=20)

class Event(models.Model):
    remote_key = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
