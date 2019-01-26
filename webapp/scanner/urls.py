from django.urls import path
from rest_framework import routers, serializers, viewsets

# ----- HTML (or whatever)
from . import views

urlpatterns = [
    path(r'test', views.TestView.as_view(), name='test'),
    path(r'scan', views.ScannerView.as_view(), name='scan'),
    path(r'config', views.ConfigView.as_view(), name='config'),
]

# ----- REST API
from .serializers import MemberViewSet, AttendanceViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'members', MemberViewSet)
router.register(r'attendance', AttendanceViewSet)
