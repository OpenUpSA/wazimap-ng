from adminsortable2.admin import SortableAdminMixin

from django.contrib.gis import admin
from django import forms

from ... import models
from wazimap_ng.general.admin.admin_base import BaseAdminModel, HistoryAdmin
from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.forms import HistoryAdminForm


class IndicatorCategoryAdminForm(HistoryAdminForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

@admin.register(models.IndicatorCategory)
class IndicatorCategoryAdmin(SortableAdminMixin, BaseAdminModel, HistoryAdmin):
    list_display = ("name", "profile", "order")
    list_filter = (filters.ProfileFilter,)

    fieldsets = (
        ("", {
            'fields': ('profile', 'name', "description", "icon", )
        }),
    )
    form = IndicatorCategoryAdminForm

