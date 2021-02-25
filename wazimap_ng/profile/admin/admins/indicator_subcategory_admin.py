from adminsortable2.admin import SortableAdminMixin
from django.contrib.gis import admin

from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.widgets import customTitledFilter, description

from ... import models


class CategoryProfileFilter(filters.ProfileFilter):
    parameter_name = 'category__profile'
    lookup_fileds = ["category__profile", "category__profile"]

@admin.register(models.IndicatorSubcategory)
class IndicatorSubcategoryAdmin(SortableAdminMixin, BaseAdminModel):
    list_display = ("name", "category", description("Profile", lambda x: x.category.profile), "order")
    list_filter = (filters.CategoryFilter, CategoryProfileFilter)
