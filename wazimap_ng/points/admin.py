from django.contrib.gis import admin
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields
from django.contrib import  messages

from django_q.tasks import async_task
from wazimap_ng.datasets import hooks


from . import models

admin.site.register(models.Theme)

def assign_to_category_action(category):
    def assign_to_category(modeladmin, request, queryset):
        queryset.update(category=category)
        messages.info(request, "Locations assigned to category {0}".format(category.name))

    assign_to_category.short_description = "Assign to {0}".format(category.name)
    assign_to_category.__name__ = 'assign_to_category_{0}'.format(category.id)

    return assign_to_category

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

    def get_actions(self, request):
        actions = super().get_actions(request)

        for category in models.Category.objects.all():
            action = assign_to_category_action(category)
            actions[action.__name__] = (
                action, action.__name__, action.short_description
            )

        return actions

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