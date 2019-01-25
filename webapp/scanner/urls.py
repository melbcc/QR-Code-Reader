from django.urls import path
from rest_framework import routers, serializers, viewsets

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

# ----- REST API
from .serializers import MemberViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'members', MemberViewSet)
