from django.contrib.gis import admin
from .. import models

from .admins import (
    LogoAdmin, ProfileIndicatorAdmin, ProfileKeyMetricsAdmin, ProfileHighlightAdmin,
    IndicatorCategoryAdmin, IndicatorSubcategoryAdmin, ProfileAdmin
)

admin.site.register(models.IndicatorCategory)
admin.site.register(models.IndicatorSubcategory)


