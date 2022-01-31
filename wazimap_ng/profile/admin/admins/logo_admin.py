from django.contrib.gis import admin

from ... import models
from wazimap_ng.general.services import permissions
from wazimap_ng.general.admin.admin_base import BaseAdminModel, HistoryAdmin
from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.forms import HistoryAdminForm

@admin.register(models.Logo)
class LogoAdmin(BaseAdminModel, HistoryAdmin):
    list_display = ("profile",)
    list_filter = (filters.ProfileFilter,)
    fieldsets = (
        ("", {
            'fields': ('profile', 'logo', "url", )
        }),
    )
    form = HistoryAdminForm