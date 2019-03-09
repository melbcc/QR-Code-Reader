from rest_framework import serializers, viewsets, generics
from django.utils import timezone

from .models import Member
from .models import Location
from .models import Event
from .models import Attendance


# ---------- Members
class MemberSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    membership_num = serializers.CharField()
    contact_id = serializers.CharField()
    status = serializers.CharField()
    status_isok = serializers.BooleanField()

class MemberViewSetByCID(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    lookup_field = 'contact_id'

class MemberViewSetByMemNo(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    lookup_field = 'membership_num'


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
class AttendanceSerializer(serializers.Serializer):
    member = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all())
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    checkin_time = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        obj = Attendance(checkin_time=timezone.now(), **validated_data)
        obj.save()
        return obj


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
