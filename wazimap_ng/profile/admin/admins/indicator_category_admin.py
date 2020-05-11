from adminsortable2.admin import SortableAdminMixin

from django.contrib.gis import admin

from ... import models
from wazimap_ng.general.admin.admin_base import BaseAdminModel

@admin.register(models.IndicatorCategory)
class IndicatorCategoryAdmin(SortableAdminMixin, BaseAdminModel):
    list_display = ("name", "profile", "order")
    list_filter = ("profile",)

