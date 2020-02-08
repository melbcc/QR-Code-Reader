from django.urls import path
from rest_framework import routers, serializers, viewsets

# ----- HTML (or whatever)
from . import views

urlpatterns = [
    path(r'', views.RootView.as_view(), name='index'),
    path(r'config/location', views.ConfigLocationView.as_view(), name='scanner-config-location'),
    path(r'config/events', views.ConfigEventsView.as_view(), name='scanner-config-events'),
    path(r'scan', views.ScannerView.as_view(), name='scanner-scan'),
    path(r'att', views.AttendanceSelect.as_view(), name='attendance-select'),
    path(r'att/<int:event_pk>', views.AttendanceList.as_view(), name='attendance-list'),
    path(r'att/<int:event_pk>/csv', views.AttendanceListCSV.as_view(), name='attendance-csv'),
    path(r'power/confirm', views.PowerConfirmationView.as_view(), name='power-confirm'),
    path(r'power/off', views.PowerOffView.as_view(), name='power-off'),
    path(r'power/restart', views.PowerRestartView.as_view(), name='power-restart'),
]

# ----- REST API
from .serializers import ContactViewSet
from .serializers import MembershipViewSetByCID, MembershipViewSetByMemNo
from .serializers import AttendanceViewSet
from .serializers import LocBlockViewSet
from .serializers import EventViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'contact', ContactViewSet)
router.register(r'members_cid', MembershipViewSetByCID)
router.register(r'members_memno', MembershipViewSetByMemNo)
router.register(r'attendance', AttendanceViewSet)
router.register(r'loc_block', LocBlockViewSet)
router.register(r'events', EventViewSet)
