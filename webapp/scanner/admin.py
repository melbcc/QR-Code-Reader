from django.contrib import admin

from .models import Member, Venue, Event, Attendance


# Register for Admin
admin.site.register(Member)
admin.site.register(Venue)
admin.site.register(Event)
admin.site.register(Attendance)
