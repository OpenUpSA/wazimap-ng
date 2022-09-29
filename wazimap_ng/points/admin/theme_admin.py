from adminsortable2.admin import SortableAdminMixin
from django.contrib.gis import admin
from django import forms

from wazimap_ng.general.admin.admin_base import BaseAdminModel, HistoryAdmin
from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.forms import HistoryAdminForm

from icon_picker_widget.widgets import IconPickerWidget

from .. import models


class ThemeAdminForm(HistoryAdminForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = IconPickerWidget()


@admin.register(models.Theme)
class ThemeAdmin(SortableAdminMixin, BaseAdminModel, HistoryAdmin):
    list_display = ("name", "profile", "order")
    list_filter = (filters.ProfileFilter,)

    fieldsets = (
        ("", {
            'fields': ('profile', 'name', "icon", "color")
        }),
    )

    form = ThemeAdminForm
    search_fields = ("name", )

    class Media:
        css = {
             'all': ('/static/css/admin-custom.css',)
        }
