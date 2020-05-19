from django.contrib.gis import admin

from ... import models
from wazimap_ng.general.services import permissions
from wazimap_ng.general.admin.admin_base import BaseAdminModel

@admin.register(models.Logo)
class LogoAdmin(BaseAdminModel):
    list_display = ("profile",)
    list_filter = ("profile",)