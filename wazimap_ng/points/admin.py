#from django.contrib import admin
from django.contrib.gis import admin
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields
from . import models

admin.site.register(models.Category)

@admin.register(models.Location)
class LocationAdmin(admin.OSMGeoAdmin):
  formfield_overrides = {
    fields.JSONField: {"widget": JSONEditorWidget},
  }

  list_display = ("name", "category",)
  list_filter = ("category",)
