from django.contrib.gis import admin
from django import forms

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.general.admin import filters
from wazimap_ng.profile.models import Profile

from icon_picker_widget.widgets import IconPickerWidget

from .. import models

class ThemeAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = IconPickerWidget()


@admin.register(models.Theme)
class ThemeAdmin(BaseAdminModel):
    list_display = ("name", "profile",)
    list_filter = (filters.ProfileFilter,)

    form = ThemeAdminForm