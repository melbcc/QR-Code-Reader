from rest_framework import serializers, viewsets, generics

from .models import Member
from .models import Location
from .models import Event
from .models import Attendance


# ---------- Members
class MemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Member
        fields = ('first_name', 'last_name', 'membership_num', 'status_id')


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    lookup_field = 'contact_id'


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
    is_upcoming = serializers.BooleanField()
    start_time_epoch = serializers.IntegerField()

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


# ---------- Attendance
class AttendanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attendance
        fields = ('pk',)  # FIXME
        #fields = ('member', 'event')


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
