from django.contrib import admin
from apps.statistics.models import DataPoint, DataSource


class DataPointAdmin(admin.ModelAdmin):
    pass


class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'data_type', 'description')


admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(DataSource, DataSourceAdmin)