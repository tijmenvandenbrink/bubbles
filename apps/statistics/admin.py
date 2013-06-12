from django.contrib import admin
from apps.statistics.models import DataPoint, DataSource


class DataPointAdmin(admin.ModelAdmin):
    list_display = ('data_source', 'service', 'start', 'end', 'value')
    list_filter = ('data_source', 'service', 'start', 'end')
    list_display_links = ('service', 'start', 'end', 'value')


class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'data_type', 'description')


admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(DataSource, DataSourceAdmin)