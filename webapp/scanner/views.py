import re
import json
import csv

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import generic, View
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder

from .models import Event, Attendance, LocBlock
from .serializers import EventSerializer, LocBlockSerializer
from .conf import settings


class RootView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['version'] = settings.VERSION
        return context


# ---------- Session Management
# TODO: instead of using request.GET or request.POST to
# populate request.sesson, could we use requests.COOKIES instead?
def std_session(request):
    # Location: loc (either an int, or None)
    if request.GET.get('clear_location', None):
        request.session['loc_blocks'] = []

    loc_block_pks = request.session['loc_blocks'] = [
        int(key[3:])
        for key in request.GET.keys()
        if re.search(r'^loc\d+$', key)
    ]
    if loc_block_pks:
        request.session['loc_blocks'] = loc_block_pks

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


def get_loc_blocks(request):
    # Get location and relevant events
    loc_block_pks = request.session.get('loc_blocks', [])
    loc_blocks = []
    if loc_block_pks:
        loc_blocks = LocBlock.objects.filter(
            pk__in=loc_block_pks
        )
    return loc_blocks


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
        # Locations QuerySet
        loc_block = LocBlock.objects.all()

        # Render & Return
        return render(request, self.template_name, {
            'locations': loc_block,
        })


class ConfigEventsView(View):
    template_name = 'config-events.html'

    def get(self, request, *args, **kwargs):
        std_session(request)

        loc_blocks = get_loc_blocks(request)
        events = Event.objects.filter(is_template=False)
        if loc_blocks:
            events = events.filter(loc_block__in=loc_blocks)
        events = [e for e in events if e.is_active]

        # Render & Return
        return render(
            request,
            self.template_name, {
                'location': loc_blocks,
                'events': events,
            },
        )

# ---------- Scanner
class ScannerView(View):
    template_name = 'scanner.html'

    def get(self, request, *args, **kwargs):
        std_session(request)

        # Get Objects from Session
        loc_blocks = get_loc_blocks(request)
        events = get_events(request)

        # Serialize Objects
        loc_blocks_ser = None
        if loc_blocks:
            loc_blocks_ser = [
                LocBlockSerializer(loc_block).data
                for loc_block in loc_blocks
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
                'locations': loc_blocks,
                'events': events,
                # Jsonified Objects (for javascript)
                'locations_json': json.dumps(loc_blocks_ser, cls=DjangoJSONEncoder),
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
