from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .indicator_data_admin import IndicatorDataAdmin
from .dataset_admin import DatasetAdmin
from .indicator_admin import IndicatorAdmin
from .dataset_file_admin import DatasetFileAdmin
from .group_admin import GroupAdmin
from .. import models


@admin.register(models.Geography)


class GeographyAdmin(TreeAdmin):
    form = movenodeform_factory(models.Geography)
    list_display = (
        "name", "code", "level", "version"
    )

    search_fields = ("name", "code")
    list_filter = ("level", "version")

@admin.register(models.GeographyHierarchy)
class GeographyHierarchyAdmin(admin.ModelAdmin):
    autocomplete_fields = ['root_geography']


@admin.register(models.Universe)
class UniverseAdmin(admin.ModelAdmin):
  formfield_overrides = {
    fields.JSONField: {"widget": JSONEditorWidget},
  }
  
@admin.register(models.Licence)
class LicenceAdmin(admin.ModelAdmin):
    pass
