from django.contrib.gis import admin

from .. import models

from .admins import LogoAdmin, ProfileIndicatorAdmin, ProfileKeyMetricsAdmin, ProfileHighlightAdmin

admin.site.register(models.IndicatorCategory)
admin.site.register(models.IndicatorSubcategory)
admin.site.register(models.Profile)



