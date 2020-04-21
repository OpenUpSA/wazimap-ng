from adminsortable2.admin import SortableAdminMixin

from django.contrib.gis import admin

from ... import models

@admin.register(models.IndicatorCategory)
class IndicatorCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "profile", "order")
    list_filter = ("profile",)

