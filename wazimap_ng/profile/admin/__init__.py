from django.contrib.gis import admin

from .. import models

from .admins import LogoAdmin, ProfileIndicatorAdmin, ProfileKeyMetricsAdmin, ProfileHighlightAdmin, IndicatorCategoryAdmin

admin.site.register(models.IndicatorSubcategory)
admin.site.register(models.Profile)



