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
from ...boundaries.models import GeographyBoundary


class GeographyBoundaryInline(admin.TabularInline):
    model = GeographyBoundary
    exclude = ("geom", "geom_cache", "area",)
    readonly_fields = ("version",)
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(models.Geography)
class GeographyAdmin(TreeAdmin):
    form = movenodeform_factory(models.Geography)

    def hierarchy(obj):
        return ", ".join(h.name for h in obj.get_root().geographyhierarchy_set.all())

    list_display = (
        "name", "code", "level", hierarchy, "created", "updated"
    )

    search_fields = ("name", "code")
    list_filter = ("level", "geographyboundary__version")

    inlines = (GeographyBoundaryInline,)


@admin.register(models.GeographyHierarchy)
class GeographyHierarchyAdmin(admin.ModelAdmin):
    autocomplete_fields = ['root_geography']
    list_display = (
        "name", "created", "updated"
    )


@admin.register(models.Universe)
class UniverseAdmin(admin.ModelAdmin):
  formfield_overrides = {
    fields.JSONField: {"widget": JSONEditorWidget},
  }
  list_display = (
        "label", "created", "updated"
    )

@admin.register(models.Licence)
class LicenceAdmin(admin.ModelAdmin):
    list_display = (
        "name", "created", "updated"
    )


@admin.register(models.Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = (
        "name", "created", "updated"
    )
