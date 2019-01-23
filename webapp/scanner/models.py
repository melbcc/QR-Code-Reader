from django.db import models


class Member(models.Model):
    # Personal Data
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20)

    # Membership & Status
    membshipnum = models.CharField(max_length=20)
    end_date = models.DateTimeField('membership end', null=True)
    status_id = models.IntegerField(null=True)

    def __repr__(self):
        return "<{cls}: {first_name} {last_name} [{membshipnum}]>".format(
            cls=type(self).__name__,
            first_name=self.first_name,
            last_name=self.last_name,
            membshipnum=self.membshipnum,
        )

    @property
    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in (
                'pk',
                'first_name', 'last_name', 'postal_code',
                'membshipnum', 'end_date', 'status_id',
            )
        }

class Venue(models.Model):
    name = models.CharField(max_length=200, blank=True)
    key = models.CharField(max_length=20)

class Event(models.Model):
    title = models.CharField(max_length=200)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
