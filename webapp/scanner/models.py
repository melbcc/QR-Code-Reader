from datetime import datetime, timedelta
import pytz

from django.db import models
from django.db.models import Q
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from .conf import settings


# ================================================
#          CiviCRM Mirrored Models
# ================================================
# All models with a 'remote_key' parameter are intended to be a partial
# mirror of the CiviCRM database.
# The 'remote_key' links the unique database entries on the remote system with
# the duplicate copied onto the RaspberryPi's local database.

civicrm_tables = {}

def civicrm_clone(cls):
    assert getattr(cls, 'remote_key', None) is not None, "{} model must have 'remote_key'".format(cls)
    if getattr(cls, 'import_order', None) is None:
        cls.import_order = 999
    civicrm_tables[cls.__name__.lower()] = cls
    return cls


@civicrm_clone
class MembershipType(models.Model):
    remote_key = models.CharField(max_length=20, null=True, blank=True)  # CiviCRM primary key
    name = models.CharField(max_length=200)
    allow_event_entry = models.BooleanField(default=True)

    import_order = 10
    remote_fieldmap = {  # <remote_field>: (<local_field>, <method>),
        'name': ('name', lambda v: v),
    }

    def __str__(self):
        return self.name


@civicrm_clone
class MembershipStatus(models.Model):
    remote_key = models.CharField(max_length=20, null=True, blank=True)  # CiviCRM primary key
    name = models.CharField(max_length=200)
    label = models.CharField(max_length=200)
    is_active = models.BooleanField(default=False)

    import_order = 11
    remote_fieldmap = {  # <remote_field>: (<local_field>, <method>),
        'name': ('name', lambda v: v),
        'label': ('label', lambda v: v),
        'is_active': ('is_active', lambda v: v),
    }

    def __str__(self):
        return self.name


@civicrm_clone
class ParticipantStatusType(models.Model):
    remote_key = models.CharField(max_length=20, null=True, blank=True)  # CiviCRM primary key
    name = models.CharField(max_length=40)

    import_order = 12
    remote_fieldmap = {  # <remote_field>: (<local_field>, <method>),
        'name': ('name', lambda v: v),
    }


@civicrm_clone
class Contact(models.Model):
    remote_key = models.CharField(max_length=20, null=True, blank=True)  # CiviCRM primary key
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    membership_num = models.CharField(max_length=20, blank=True, null=True)  # custom_8

    import_order = 20
    remote_fieldmap = {  # <remote_field>: (<local_field>, <method>),
        'first_name': ('first_name', lambda v: v),
        'last_name': ('last_name', lambda v: v),
        'custom_8': ('membership_num', lambda v: v),
    }

    # Guest Data
    #   If an instance of a Contact has no 'remote_key', then they're
    #   a guest; assumed to not already eixst as a contact.
    email_address = models.EmailField(max_length=200, null=True, blank=True)
    mobile_number = PhoneNumberField(blank=True)

    def __str__(self):
        return '{first_name} {last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name,
        )


@civicrm_clone
class Membership(models.Model):
    remote_key = models.CharField(max_length=20)  # CiviCRM primary key
    end_date = models.DateTimeField('membership end', null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    status = models.ForeignKey(MembershipStatus, on_delete=models.CASCADE, null=True, blank=True)
    type = models.ForeignKey(MembershipType, on_delete=models.CASCADE, null=True, blank=True)

    import_order = 30
    remote_fieldmap = {  # <remote_field>: (<local_field>, <method>),
        'contact_id': ('contact', lambda v: Contact.objects.filter(remote_key=v).first()),
        'end_date': ('end_date', lambda v: pytz.timezone(settings.TIME_ZONE).localize(datetime.strptime(v, '%Y-%m-%d')) if v else v),
        'membership_type_id': ('type', lambda v: MembershipType.objects.get(remote_key=v)),
        'status_id': ('status', lambda v: MembershipStatus.objects.get(remote_key=v)),
    }

    @property
    def status_isok(self):
        return (self.status.name in ('Grace', 'Current'))

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


#@civicrm_clone
class Location(models.Model):
    remote_key = models.CharField(max_length=20)
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


@civicrm_clone
class Event(models.Model):
    remote_key = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    start_time = models.DateTimeField('start time')
    end_time = models.DateTimeField('end time', null=True, blank=True)

    import_order = 5
    remote_fieldmap = {  # <remote_field>: (<local_field>, <method>),
        'title': ('title', lambda v: v),
        'start_date': ('start_time', lambda v: pytz.timezone(settings.TIME_ZONE).localize(datetime.strptime(v, '%Y-%m-%d %H:%M:%S'))),
        'end_date': ('end_time', lambda v: pytz.timezone(settings.TIME_ZONE).localize(datetime.strptime(v, '%Y-%m-%d %H:%M:%S')) if v else v),
    }

    @classmethod
    def remote_cleanup_queryset(cls):
        now = pytz.timezone(settings.TIME_ZONE).normalize(timezone.now())
        return cls.objects.filter(
            Q(start_time__range=[(now + timedelta(days=x)) for x in (-7, 14)]) or
            (Q(start_time__lt=now) and Q(end_time__gt=now))
        ).exclude(
            pk__in=Attendance.objects.filter(export_time__isnull=True).values_list('event__pk', flat=True)
        )

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        """True if event is a plausible candidate for a scanner"""
        # Threshold times surrounding event
        active_start = self.start_time - timedelta(seconds=settings.SCANNER_EVENT_ACTIVE_BEFORE)
        active_end = self.start_time + timedelta(
            seconds=settings.SCANNER_EVENT_ACTIVE_DEFAULT_DURATION + settings.SCANNER_EVENT_ACTIVE_AFTER
        )
        if self.end_time:
            active_end = self.end_time + timedelta(seconds=settings.SCANNER_EVENT_ACTIVE_AFTER)

        # Is the current time within bounds of the event
        now = pytz.timezone(settings.TIME_ZONE).normalize(timezone.now())
        return (active_start <= now <= active_end)

    @property
    def is_long(self):
        if self.end_time:
            delta = timedelta(seconds=settings.SCANNER_EVENT_LONG_DURATION)
            return ((self.end_time - self.start_time) >= delta)
        return False

    @property
    def start_time_epoch(self):
        return self.start_time.timestamp()


# ================================================
#          Local Only Models
# ================================================
# as opposed to those above that are mirrored from CiviCRM

class Attendance(models.Model):
    """
    Attendance is the equivalent of the Participant table in CiviCRM.

    Its name is different because it's not a mirror of CiviCRM, but a log
    of membership "scans" to be uploaded to CiviCRM periodically.

    For more information::

        ./manage.py export_attendance --help
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    checkin_time = models.DateTimeField('checkin time', null=True, blank=True)
    export_time = models.DateTimeField('upload time', null=True, blank=True)
