from django.contrib import admin

from .models import Member, Venue, Event, Attendance


# Register for Admin
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('membership_num', 'first_name', 'last_name')

admin.site.register(Venue)
admin.site.register(Event)
admin.site.register(Attendance)
