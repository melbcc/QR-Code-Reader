from rest_framework import serializers, viewsets, generics

from .models import Member, Attendance


# ---------- Members
class MemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Member
        fields = ('first_name', 'last_name', 'membership_num', 'status_id')


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    lookup_field = 'contact_id'


# ---------- Events



# ---------- Attendance
class AttendanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attendance
        fields = ('pk',)  # FIXME
        #fields = ('member', 'event')


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
