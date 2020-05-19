from django.contrib.gis import admin
from adminsortable2.admin import SortableAdminMixin

from wazimap_ng.admin_utils import customTitledFilter, description

from ... import models
from wazimap_ng.general.admin.admin_base import BaseAdminModel


@admin.register(models.IndicatorSubcategory)
class IndicatorSubcategoryAdmin(SortableAdminMixin, BaseAdminModel):
    list_display = ("name", "category", description("Profile", lambda x: x.category.profile), "order")
    list_filter = ("category", "category__profile")

