from adminsortable2.admin import SortableAdminMixin
from django import forms
from django.contrib.gis import admin
from icon_picker_widget.widgets import IconPickerWidget

from wazimap_ng.general.admin import filters
from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.points.models import Theme


class ThemeAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = IconPickerWidget()


@admin.register(Theme)
class ThemeAdmin(SortableAdminMixin, BaseAdminModel):
    list_display = ("name", "profile", "order")
    list_filter = (filters.ProfileFilter,)

    form = ThemeAdminForm
    search_fields = ("name", )

    class Media:
        css = {
            'all': ('/static/css/admin-custom.css',)
        }
