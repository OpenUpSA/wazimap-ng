from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .indicator_data_admin import IndicatorDataAdmin
from .dataset_admin import DatasetAdmin
from .indicator_admin import IndicatorAdmin
from .. import models


admin.site.register(models.IndicatorCategory)
admin.site.register(models.IndicatorSubcategory)
admin.site.register(models.Profile)

@admin.register(models.Geography)
class GeographyAdmin(TreeAdmin):
    form = movenodeform_factory(models.Geography)
    list_display = (
        "name", "code", "level"
    )

    list_filter = ("level",)


@admin.register(models.Universe)
class UniverseAdmin(admin.ModelAdmin):
  formfield_overrides = {
    fields.JSONField: {"widget": JSONEditorWidget},
  }
