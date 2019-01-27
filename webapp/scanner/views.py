from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic, View

from .models import Location, Event


class RootView(generic.TemplateView):
    template_name = 'index.html'


# ---------- Configure
class ConfigLocationView(View):
    template_name = 'config-location.html'

    def get(self, request, *args, **kwargs):
        # Locations QuerySet
        locations = Location.objects.all()

        # Render & Return
        return render(request, self.template_name, {
            'locations': locations,
        })


class ConfigEventsView(View):
    template_name = 'config-events.html'

    def get(self, request, *args, **kwargs):
        # Get location and relevant events
        location = Location.objects.filter(pk=int(request.GET['loc'])).first()
        events = Event.objects.filter(location=location)
        events = [e for e in events if e.is_upcoming]

        # Render & Return
        return render(request, self.template_name, {
            'location': location,
            'events': events,
        })

# ---------- Scanner
class ScannerView(generic.TemplateView):
    template_name = 'scanner.html'
