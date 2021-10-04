from adminsortable2.admin import SortableAdminMixin
from django import forms
from django.contrib.gis import admin

from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel

from ... import models


class IndicatorCategoryAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@admin.register(models.IndicatorCategory)
class IndicatorCategoryAdmin(SortableAdminMixin, BaseAdminModel):
    list_display = ("name", "profile", "order")
    list_filter = (filters.ProfileFilter,)
    form = IndicatorCategoryAdminForm
