from django.contrib import admin
from django.utils.html import format_html

from .models import MembershipType, MembershipStatus
from .models import Contact, Membership, Location, Event, Attendance


@admin.register(MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'allow_event_entry')
    search_fields = ('name',)


@admin.register(MembershipStatus)
class MembershipStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'is_active')
    search_fields = ('name', 'label')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'contact_id', 'membership_num',
    )
    search_fields = (
        'first_name', 'last_name', 'remote_key', 'membership_num',
    )

    def contact_id(self, obj):
        return obj.remote_key


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = (
        'contact', 'membership_num', 'contact_id', 'type', 'status_pill',
    )
    search_fields = (
        'contact__membership_num', 'contact__remote_key',
        'contact__first_name', 'contact__last_name',
    )

    STATUS_PILL_STYLE = {
        'CURRENT': ['background: #090', 'color: #fff', 'font-weight: bold'],
        'GRACE': ['background: #e90', 'color: #fff', 'font-weight: bold'],
        'EXPIRED': ['background: #d00', 'color: #fff', 'font-weight: bold'],
        'DECEASED': ['background: #aaa', 'color: #fff', 'font-weight: bold'],
    }
    def status_pill(self, obj):
        return format_html('<div style="{style}">{text}</div>'.format(
            style=';'.join([
                'text-align: center',
                'border-radius: 0.5em',
                'width: 8em',
            ] + self.STATUS_PILL_STYLE.get(getattr(obj.status, 'name', '').upper(), [])),
            text=obj.status,
        ))

    status_pill.allow_tags = True

    def contact_id(self, obj):
        return obj.contact.remote_key


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('remote_key', 'name')
    search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('remote_key', 'start_time', 'end_time', 'title', 'is_upcoming_pill')
    search_fields = ('title', 'location__name')

    def is_upcoming_pill(self, obj):
        is_upcoming = obj.is_upcoming
        return format_html('<div style="{style}">{text}</div>'.format(
            style=';'.join([
                'text-align: center',
                'border-radius: 0.4em',
                'width: 8em',
                'font-weight: bold',
                'color: #fff',
                'background: {}'.format('green' if is_upcoming else 'red'),
            ]),
            text="{!r}".format(is_upcoming),
        ))


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'contact', 'checkin_time', 'export_time')
    search_fields = (
        'event__title',
        'contact__first_name', 'contact__last_name',
        'contact__membership_num', 'contact__remote_key',
    )
