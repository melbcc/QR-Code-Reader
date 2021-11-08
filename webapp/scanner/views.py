import re
import json
import csv
from collections import defaultdict

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import generic, View
from django.template import RequestContext
from django.core.serializers.json import DjangoJSONEncoder

from .models import Event, Attendance, Address
from .serializers import EventSerializer, AddressSerializer
from .conf import settings


def root(request):
    if request.user.is_authenticated:
        return redirect('/app/select')
    return redirect('/login')


# ---------- Session Management
# TODO: instead of using request.GET or request.POST to
# populate request.sesson, could we use requests.COOKIES instead?
def std_session(request):
    # Location: loc (either an int, or None)
    if request.GET.get('clear_location', None):
        request.session['addresses'] = []

    address_pks = request.session['addresses'] = [
        int(key[4:])  # everything after 'addr'
        for key in request.GET.keys()
        if re.search(r'^addr\d+$', key)
    ]
    if address_pks:
        request.session['addresses'] = address_pks

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


def get_addresses(request):
    # Get location and relevant events
    address_pks = request.session.get('addresses', [])
    addresses = []
    if address_pks:
        addresses = Address.objects.filter(
            pk__in=address_pks
        )
    return addresses


def get_events(request, only_upcoming=True):
    event_pks = request.session.get('events', [])
    if event_pks:
        events = Event.objects.filter(pk__in=event_pks)
    else:
        events = []

    # FIXME: filter queryset filter, this is a slow way to do this.
    if only_upcoming:
        events = [e for e in events if e.is_active]

    return events


# ---------- Configure
class ConfigLocationView(View):
    template_name = 'config-location.html'

    def get(self, request, *args, **kwargs):
        # Render & Return
        return render(request, self.template_name, {
            'addresses': Address.objects.filter(
                pk__in=Event.objects.are_active().values_list('loc_block__address', flat=True).distinct()
            ),
        })


class ConfigEventsView(View):
    template_name = 'config-events.html'

    def get(self, request, *args, **kwargs):
        std_session(request)

        addresses = get_addresses(request)
        events = Event.objects.filter(is_template=False).are_active()
        if addresses:
            events = events.filter(loc_block__address__in=addresses)

        # Render & Return
        return render(
            request,
            self.template_name, {
                'location': defaultdict(lambda: (lambda: '(multiple)'), {
                    0: lambda: None,
                    1: lambda: addresses.first(),
                })[addresses.count() if addresses else 0](),
                'events': events,
            },
        )


# ---------- Scanner
class ScannerView(View):
    template_name = 'scanner.html'

    def get(self, request, *args, **kwargs):
        std_session(request)

        # Get Objects from Session
        addresses = get_addresses(request)
        events = get_events(request)

        # Serialize Objects
        addresses_ser = None
        if addresses:
            addresses_ser = [
                AddressSerializer(a).data
                for a in addresses
            ]
        events_ser = []
        if events:
            events_ser = [EventSerializer(e).data for e in events]

        # Render & Return
        return render(
            request,
            self.template_name,
            {
                # Objects
                'locations': addresses,
                'events': events,
                # Jsonified Objects (for javascript)
                'locations_json': json.dumps(addresses_ser, cls=DjangoJSONEncoder),
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
class PowerConfirmationView(generic.TemplateView):
    template_name = "power-confirm.html"


class _PowerView(View):
    template_name = "power-execute.html"

    def get(self, request, *args, **kwargs):
        import subprocess
        proc = subprocess.call(self.CMD, shell=True)
        return render(request, self.template_name, {
            'message': self.MESSAGE,
        })

class PowerOffView(_PowerView):
    MESSAGE = "Powering Down"
    CMD = "sudo /sbin/poweroff"

class PowerRestartView(_PowerView):
    MESSAGE = "Restarting"
    CMD = "sudo /sbin/reboot"


# ---------- CSRF Token
def get_csrf_token(request):
    from django.http import JsonResponse
    from django.middleware import csrf
    # ref: https://stackoverflow.com/questions/43567052#43567080
    token = csrf.get_token(request)
    return JsonResponse({'token': token})