from django.contrib.gis import admin

from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel

from ... import models


@admin.register(models.Logo)
class LogoAdmin(BaseAdminModel):
    list_display = ("profile",)
    list_filter = (filters.ProfileFilter,)
