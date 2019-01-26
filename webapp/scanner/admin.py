from django.contrib import admin

from .models import Member, Location, Event, Attendance


# Register for Admin
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'membership_num', 'contact_id',
        'first_name', 'last_name', 'status_id',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('remote_key', 'name')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('remote_key', 'start_time', 'title', 'location')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'member')
