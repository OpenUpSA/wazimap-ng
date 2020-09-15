from django.contrib.gis import admin

from ... import models
from wazimap_ng.general.services import permissions
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.admin import filters


@admin.register(models.Logo)
class LogoAdmin(BaseAdminModel):
    list_display = ("profile",)
    list_filter = (filters.ProfileFilter,)
