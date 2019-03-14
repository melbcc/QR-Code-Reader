from django.conf import settings
from appconf import AppConf

class ScannerConf(AppConf):
    # --- Event Settings
    # "upcoming" status is true for a period surrounding the event's start time
    EVENT_UPCOMING_BEFORE = 6 * (60 * 60)  # (unit: seconds)
    EVENT_UPCOMING_AFTER = 12 * (60 * 60)  # (unit: seconds)

    # --- Attendance Settings
    # Time after attendance is uploaded to CiviCRM that it can be purged
    ATTENDANCE_PURGE_TIMEOUT = 24 * (60 * 60)  # (unit: seconds)
