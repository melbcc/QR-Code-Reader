from django.urls import path
from rest_framework import routers, serializers, viewsets

# ----- HTML (or whatever)
from . import views

urlpatterns = [
    path(r'test', views.TestView.as_view(), name='scanner-test'),
    path(r'scan', views.ScannerView.as_view(), name='scanner-scan'),
    path(r'', views.ConfigView.as_view(), name='scanner-config'),
]

# ----- REST API
from .serializers import MemberViewSet
from .serializers import AttendanceViewSet
from .serializers import LocationViewSet
from .serializers import EventViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'members', MemberViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'events', EventViewSet)
