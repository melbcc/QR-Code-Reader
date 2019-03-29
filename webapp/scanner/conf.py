from django.conf import settings
from appconf import AppConf

class ScannerConf(AppConf):
    # --- Event Settings
    # "active" status is true for a period surrounding the event's start time
    EVENT_ACTIVE_BEFORE = 6 * (60 * 60)  # (unit: seconds)
    EVENT_ACTIVE_AFTER = 6 * (60 * 60)  # (unit: seconds)
    EVENT_ACTIVE_DEFAULT_DURATION = 3 * (60 * 60)  # (unit: seconds)

    # "long event" status is true if an event is scheduled for a long period of time
    EVENT_LONG_DURATION = 12 * (60 * 60)  # (unit: seconds)

    # --- Attendance Settings
    # Time after attendance is uploaded to CiviCRM that it can be purged
    ATTENDANCE_PURGE_TIMEOUT = 24 * (60 * 60)  # (unit: seconds)
