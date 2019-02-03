from django.contrib import admin
from django.utils.html import format_html

from .models import Member, Location, Event, Attendance


# Register for Admin
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'membership_num', 'contact_id',
        'first_name', 'last_name', 'status_pill',
    )
    search_fields = (
        'membership_num', 'contact_id', 'first_name', 'last_name',
    )

    STATUS_PILL_STYLE = {
        'CURRENT': ['background: #090', 'color: #fff', 'font-weight: bold'],
        'GRACE': ['background: #e90', 'color: #fff', 'font-weight: bold'],
        'EXPIRED': ['background: #d00', 'color: #fff', 'font-weight: bold'],
        'DECEASED': ['background: #aaa', 'color: #fff', 'font-weight: bold'],
    }
    def status_pill(self, obj):
        status_name = Member.STATUS_ID_CHOICES[obj.status_id]
        return format_html('<div style="{style}">{text}</div>'.format(
            style=';'.join([
                'text-align: center',
                'border-radius: 0.4em',
                'width: 8em',
            ] + self.STATUS_PILL_STYLE.get(status_name, [])),
            text=status_name,
        ))

    status_pill.allow_tags = True


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('remote_key', 'name')
    search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('remote_key', 'start_time', 'title', 'location', 'is_upcoming_pill')
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
    list_display = ('event', 'member', 'checkin_time')
    search_fields = (
        'event__title',
        'member__first_name', 'member__last_name',
        'member__membership_num', 'member__contact_id',
    )
