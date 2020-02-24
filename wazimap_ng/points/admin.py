#from django.contrib import admin
from django.contrib.gis import admin
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields

from django_q.tasks import async_task
from wazimap_ng.datasets import hooks


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

@admin.register(models.CoordinateFile)
class CoordinateFileAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        is_created = obj.pk == None and change == False
        super().save_model(request, obj, form, change)
        if is_created:
            async_task(
                "wazimap_ng.points.tasks.process_uploaded_file",
                obj, "Location",
                task_name=f"Uploading data: {obj.title}",
                hook="wazimap_ng.datasets.hooks.notify_user",
                key=request.session.session_key,
                type="file_upload",
            )
            hooks.custom_admin_notification(
                request.session,
                "info",
                "Data upload for %s started. We will let you know when process is done." % (
                    obj.title
                )
            )
        return obj