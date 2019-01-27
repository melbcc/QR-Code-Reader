from django.contrib import admin

from .models import Member, Location, Event, Attendance


# Register for Admin
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'membership_num', 'contact_id',
        'first_name', 'last_name', 'status_id',
    )
    search_fields = (
        'membership_num', 'contact_id', 'first_name', 'last_name',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('remote_key', 'name')
    search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('remote_key', 'start_time', 'title', 'location')
    search_fields = ('title', 'location__name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'member')
    search_fields = (
        'event__title',
        'member__first_name', 'member__last_name',
        'member__membership_num', 'member__contact_id',
    )
