from django.contrib.gis import admin
from adminsortable2.admin import SortableAdminMixin

from wazimap_ng.admin_utils import customTitledFilter, description

from ... import models

@admin.register(models.IndicatorSubcategory)
class IndicatorSubcategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "category", description("Profile", lambda x: x.category.profile), "order")
    list_filter = ("category", "category__profile")

