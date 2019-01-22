from django.db import models


class Member(models.Model):
    # Personal Data
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20)

    # Membership & Status
    membshipnum = models.CharField(max_length=20)
    end_date = models.DateTimeField('membership end')
    status_id = models.IntegerField()

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
