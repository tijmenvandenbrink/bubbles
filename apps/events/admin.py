from django.contrib import admin
from apps.events.models import Event, EventClass, EventSeverity


class EventClassAdmin(admin.ModelAdmin):
    pass


class EventSeverityAdmin(admin.ModelAdmin):
    pass


class EventAdmin(admin.ModelAdmin):
    pass


admin.site.register(Event, EventAdmin)
admin.site.register(EventClass, EventClassAdmin)
admin.site.register(EventSeverity, EventSeverityAdmin)