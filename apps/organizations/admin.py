from django.contrib import admin
from apps.organizations.models import Organization


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('org_id', 'name', 'org_abbreviation')
    search_fields = ('org_id', 'name', 'org_abbreviation')
    list_display_links = ('name',)


admin.site.register(Organization, OrganizationAdmin)