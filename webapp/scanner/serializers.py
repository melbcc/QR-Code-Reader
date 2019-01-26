from rest_framework import serializers, viewsets, generics

from .models import Member


# ---------- Members
class MemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Member
        fields = ('first_name', 'last_name', 'membership_num', 'status_id')


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    lookup_field = 'membership_num'
