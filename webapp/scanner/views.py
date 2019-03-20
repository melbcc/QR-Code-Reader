import re
import json
import csv

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import generic, View
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder

from .models import Location, Event, Attendance
from .serializers import EventSerializer, LocationSerializer

class RootView(generic.TemplateView):
    template_name = 'index.html'


# ---------- Session Management
# TODO: instead of using request.GET or request.POST to
# populate request.sesson, could we use requests.COOKIES instead?
def std_session(request):
    # Location: loc (either an int, or None)
    if request.GET.get('clear_location', None):
        request.session['location'] = None
    if 'loc' in request.GET:
        location_pk = request.GET['loc']
        if location_pk is not None:
            location_pk = int(location_pk)
        request.session['location'] = location_pk

    # Events: ev<pk>=on
    if request.GET.get('clear_events', None):
        request.session['events'] = []
    else:
        event_pks = set(
            int(k[2:])
            for (k, v) in request.GET.items()
            if (k.startswith('ev') and v.lower() == 'on')
        )
        if event_pks:
            request.session['events'] = sorted(event_pks)  # list

    # return original request (optional)
    return request


def get_location(request):
    # Get location and relevant events
    location_pk = request.session.get('location', None)
    location = None
    if location_pk is not None:
        location = Location.objects.filter(
            pk=location_pk
        ).first()
    return location


def get_events(request, only_upcoming=True):
    event_pks = request.session.get('events', [])
    if event_pks:
        events = Event.objects.filter(pk__in=event_pks)
    else:
        events = []

    # FIXME: filter queryset filter, this is a slow way to do this.
    if only_upcoming:
        events = [e for e in events if e.is_upcoming]

    return events


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
        std_session(request)

        location = get_location(request)
        events = Event.objects.all()
        if location is not None:
            events = events.filter(location=location)
        events = [e for e in events if e.is_upcoming]

        # Render & Return
        return render(
            request,
            self.template_name, {
                'location': location,
                'events': events,
            },
        )

# ---------- Scanner
class ScannerView(View):
    template_name = 'scanner.html'

    def get(self, request, *args, **kwargs):
        std_session(request)

        # Get Objects from Session
        location = get_location(request)
        events = get_events(request)

        # Serialize Objects
        location_ser = None
        if location:
            location_ser = LocationSerializer(location).data
        events_ser = []
        if events:
            events_ser = [EventSerializer(e).data for e in events]

        # Render & Return
        return render(
            request,
            self.template_name,
            {
                # Objects
                'location': location,
                'events': events,
                # Jsonified Objects (for javascript)
                'location_json': json.dumps(location_ser, cls=DjangoJSONEncoder),
                'events_json': json.dumps(events_ser, cls=DjangoJSONEncoder),
            },
        )

# ---------- Attendance List
class AttendanceSelect(View):
    template_name = 'attendance-select.html'

    def get(self, request, *args, **kwargs):
        event_pks = set(Attendance.objects.all().values_list('event', flat=True))
        events = Event.objects.filter(pk__in=event_pks)

        return render(
            request,
            self.template_name,
            {
                'events': events,
            },
        )


class AttendanceList(View):
    template_name = 'attendance-list.html'

    def get(self, request, *args, **kwargs):
        event_pk = int(kwargs['event_pk'])
        event = Event.objects.filter(pk=event_pk).first()

        return render(
            request,
            self.template_name,
            {
                'event': event,
                'records': Attendance.objects.filter(event=event),
            },
        )


class AttendanceListCSV(View):
    def get(self, request, *args, **kwargs):
        # Get event
        event_pk = int(kwargs['event_pk'])
        event = Event.objects.filter(pk=event_pk).first()

        # Set filename
        filename = "{event_title}_({datestamp}).csv".format(
            event_title=re.sub(r'[^0-9a-zA-Z]', '-', event.title),
            datestamp=event.start_time.strftime("%Y-%m-%d_%H:%M:%S"),
        )

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{filename}"'.format(
            filename=filename,
        )

        # Create CSV
        writer = csv.writer(response)
        writer.writerow(['CHECKIN_TIME', 'MEMBER', 'MEMBERSHIP_NUM', 'IS_GUEST', 'GUEST_EMAIL'])
        for att in Attendance.objects.filter(event=event):
            membership_num = ''
            is_guest = 'No'
            if att.contact.membership_num:
                membership_num = att.contact.membership_num
            else:
                is_guest = 'Yes'
            writer.writerow([
                att.checkin_time.strftime("%Y-%m-%d %H:%M:%S"),
                str(att.contact),
                membership_num,
                is_guest,
                att.contact.email_address,
            ])

        # Return HTTP response
        return response


# ---------- Power Off
class PowerOffConfirmationView(generic.TemplateView):
    template_name = "poweroff-confirm.html"


class PowerOffView(View):
    template_name = "poweroff-execute.html"

    def get(self, request, *args, **kwargs):
        import subprocess
        proc = subprocess.call("/sbin/poweroff", shell=True)
        return render(request, self.template_name)
