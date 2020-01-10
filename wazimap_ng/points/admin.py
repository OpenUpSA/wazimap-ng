#from django.contrib import admin
from django.contrib.gis import admin
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields
from . import models

admin.site.register(models.Theme)

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "theme",)
    list_filter = ("theme",)

@admin.register(models.Location)
class LocationAdmin(admin.OSMGeoAdmin):
    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
      }

    list_display = ("name", "category",)
    list_filter = ("category",)
