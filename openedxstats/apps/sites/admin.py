from __future__ import unicode_literals

from django.contrib import admin
from .models import *

# Admin classes
class SiteAdmin(admin.ModelAdmin):
    """
    Admin class for Sites.
    """
    date_heirarchy = 'last_checked'
    search_fields = ['site_type', 'name', 'org_type', 'course_type']
    list_display = ('site_type', 'name', 'url', 'course_count', 'last_checked', 'org_type',
                    'get_languages', 'get_geographies', 'github_fork', 'notes', 'course_type', 'registered_user_count',
                    'active_learner_count', 'active_start_date', 'active_end_date')


# Register models
admin.site.register(Site, SiteAdmin)
admin.site.register(Language)
admin.site.register(GeoZone)
admin.site.register(SiteLanguage)
admin.site.register(SiteGeoZone)
