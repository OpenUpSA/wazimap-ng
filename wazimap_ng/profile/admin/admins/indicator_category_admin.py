from adminsortable2.admin import SortableAdminMixin

from django.contrib.gis import admin
from django import forms

from ... import models
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.admin import filters

from icon_picker_widget.widgets import IconPickerWidget


class IndicatorCategoryAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = IconPickerWidget()


@admin.register(models.IndicatorCategory)
class IndicatorCategoryAdmin(SortableAdminMixin, BaseAdminModel):
    list_display = ("name", "profile", "order")
    list_filter = (filters.ProfileFilter,)
    form = IndicatorCategoryAdminForm

    class Media:
        css = {
            'all': ('/static/css/admin-custom.css',)
        }
