from rest_framework import serializers, viewsets, generics
from rest_framework.exceptions import NotFound
from django.utils import timezone

import re
import pytz

from .conf import settings

from .models import Contact
from .models import Membership
from .models import Location
from .models import Event
from .models import Attendance


# ---------- Contacts
class ContactSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email_address = serializers.CharField()
    mobile_number = serializers.CharField(required=False)

    # copied from http://emailregex.com ... seems legit
    EMAIL_REGEX = re.compile(r'^[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+$', re.IGNORECASE)

    def validate_email_address(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError(
                "invalid email address type: {!r} ({})".format(value, type(value))
            )
        value_clean = re.sub(r'\s', '', value)  # remove all white space
        if not self.EMAIL_REGEX.search(value_clean):
            raise serializers.ValidationError("invalid email address: {!r}".format(value))
        return value_clean

    def create(self, validated_data):
        obj = Contact(**validated_data)
        obj.save()
        return obj

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


# ---------- Members
class MembershipSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    membership_num = serializers.CharField()
    contact_id = serializers.CharField()  # nb: local database's pk for contact
    status = serializers.CharField()
    status_isok = serializers.BooleanField()

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.filter(type__allow_event_entry=True)
    serializer_class = MembershipSerializer

    def get_object(self, *args, **kwargs):
        obj = self.queryset.filter(
            **{self.lookup_field: self.kwargs[self.lookup_field].lstrip('0')}
        ).order_by('-end_date').first()

        if not obj:
            raise NotFound("No valid Membership was found")

        return obj

class MembershipViewSetByCID(MembershipViewSet):
    lookup_field = 'contact__remote_key'

class MembershipViewSetByMemNo(MembershipViewSet):
    lookup_field = 'contact__membership_num'


# ---------- Locations
class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ('pk', 'name')

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


# ---------- Events
#class EventSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = Event
#        #fields = ('pk', 'title', 'location')
#        fields = '__all__'
#    #title = serializers.CharField()

class EventSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    title = serializers.CharField()
    location = LocationSerializer()
    #email = serializers.EmailField()
    #content = serializers.CharField(max_length=200)
    #created = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    start_time_epoch = serializers.IntegerField()

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


# ---------- Attendance
class AttendanceSerializer(serializers.Serializer):
    contact = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all())
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    checkin_time = serializers.DateTimeField(read_only=True)
    export_time = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        event = validated_data['event']
        contact = validated_data['contact']

        # Find pre-recorded attendance
        obj = Attendance.objects.filter(contact=contact, event=event).first()

        if (obj is None) or event.is_long:
            obj = Attendance(  # Create record of attendance
                checkin_time=pytz.timezone(settings.TIME_ZONE).normalize(timezone.now()),
                **validated_data,
            )
            obj.save()

        return obj


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
