from django.contrib import admin
from apps.statistics.models import DataPoint, DataSource


class DataPointAdmin(admin.ModelAdmin):
    list_display = ('data_source', 'device', 'component', 'service', 'start', 'end', 'value')
    list_filter = ('service', 'device', 'component', 'start', 'end')
    search_fields = ('data_source', 'service', 'device', 'component')

    pass


class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'data_type', 'description')


admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(DataSource, DataSourceAdmin)