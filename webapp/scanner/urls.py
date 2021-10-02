from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from rest_framework import routers, serializers

# ----- HTML (or whatever)
from . import views

urlpatterns = [
    path(r'', views.RootView.as_view(), name='index'),

    # Configure Scanner
    path(r'config/location', views.ConfigLocationView.as_view(), name='scanner-config-location'),
    path(r'config/events', views.ConfigEventsView.as_view(), name='scanner-config-events'),

    # Scanner page
    path(r'scan', views.ScannerView.as_view(), name='scanner-scan'),

    # Attendance
    path(r'att', views.AttendanceSelect.as_view(), name='attendance-select'),
    path(r'att/<int:event_pk>', views.AttendanceList.as_view(), name='attendance-list'),
    path(r'att/<int:event_pk>/csv', views.AttendanceListCSV.as_view(), name='attendance-csv'),

    # Power control
    path(r'power/confirm', views.PowerConfirmationView.as_view(), name='power-confirm'),
    path(r'power/off', views.PowerOffView.as_view(), name='power-off'),
    path(r'power/restart', views.PowerRestartView.as_view(), name='power-restart'),

    # Google OAuth: ref: https://www.section.io/engineering-education/django-google-oauth/
    path('login', TemplateView.as_view(template_name="login.html")),
    path('accounts', include('allauth.urls')),
    path('logout', LogoutView.as_view()),

    path(r'token/csrf', views.get_csrf_token, name='token-csrf'),  # responds with: {'token': <token>}
]

# ----- REST API
from .serializers import ContactViewSet
from .serializers import MembershipViewSetByCID, MembershipViewSetByMemNo, MembershipSearchViewSet
from .serializers import AttendanceViewSet
from .serializers import LocBlockViewSet
from .serializers import EventViewSet, ActiveEventViewSet, EventDetailViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'contact', ContactViewSet)
router.register(r'members_cid', MembershipViewSetByCID)
router.register(r'members_memno', MembershipViewSetByMemNo)
router.register(r'membersearch', MembershipSearchViewSet, basename='membersearch')
router.register(r'attendance', AttendanceViewSet)
router.register(r'loc_block', LocBlockViewSet)
router.register(r'events', EventViewSet)
router.register(r'activeevents', ActiveEventViewSet, basename='activeevents')
router.register(r'eventdetail', EventDetailViewSet, basename='eventdetail')