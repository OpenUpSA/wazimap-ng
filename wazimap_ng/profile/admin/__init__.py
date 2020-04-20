from django.contrib.gis import admin
from .. import models

from .admins import (
    LogoAdmin, ProfileIndicatorAdmin, ProfileKeyMetricsAdmin, ProfileHighlightAdmin,
    IndicatorCategoryAdmin, IndicatorSubcategoryAdmin
)

admin.site.register(models.Profile)



