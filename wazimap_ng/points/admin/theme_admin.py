from django.contrib.gis import admin

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.profile.models import Profile

from .. import models


@admin.register(models.Theme)
class ThemeAdmin(BaseAdminModel):
    list_display = ("name", "profile",)
    list_filter = ("profile",)