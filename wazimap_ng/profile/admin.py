from django.contrib.gis import admin

from . import models

@admin.register(models.Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ("profile",)
    list_filter = ("profile",)
