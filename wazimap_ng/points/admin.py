from django.contrib.gis import admin
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields
from django.contrib import  messages
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from django_q.tasks import async_task
from django_q.models import Task
from wazimap_ng.datasets import hooks
from django.urls import reverse
from django.conf import settings
import pandas as pd

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
    list_display = ("title", "category", "get_status", )
    exclude = ("task", )

    def get_readonly_fields(self, request, obj=None):

        readonly_fields = self.readonly_fields
        if obj:
            readonly_fields = readonly_fields + ("title", "category", "get_status")
            if obj.task: 
                readonly_fields = readonly_fields + ("get_task_link",)
                if not obj.task.success:
                    readonly_fields = readonly_fields + ("get_fail_reason", )
        return readonly_fields

    def get_status(self, obj):
        if obj.task:
            return "Processed" if obj.task.success else "Failed"
        return "In Queue"

    get_status.short_description = 'Task Status'

    def get_task_link(self, obj):
        if obj.task:

            task_type = "success" if obj.task.success else "failure"
            admin_url = reverse(
                'admin:%s_%s_change' % (
                    obj.task._meta.app_label, task_type
                ),  args=[obj.task.id]
            )

            return mark_safe('<a href="%s">%s</a>' % (admin_url, obj.task.id))
        return "-"

    get_task_link.short_description = 'Task'

    def get_fail_reason(self, obj):

        if obj.task and not obj.task.success:
            result = obj.task.result
            if "CustomDataParsingExecption" in result:
                logdir = settings.MEDIA_ROOT + "/logs/points/"
                filename = "%s_%d_log.csv" % (obj.title.replace(" ", "_"), obj.id)
                download_url = settings.MEDIA_URL + "logs/points/"

                df = pd.read_csv(logdir+filename, header=None, sep=",", nrows=10, skiprows=1)
                error_list = df.values.tolist()

                result = render_to_string(
                    'custom/render_task_errors.html', { 'errors': error_list, 'download_url': download_url+filename}
                )

            return mark_safe(result)
        return "-"

    get_fail_reason.short_description = 'Task Failure Reason'

    def save_model(self, request, obj, form, change):
        is_created = obj.pk == None and change == False
        super().save_model(request, obj, form, change)
        if is_created:
            task_id = async_task(
                "wazimap_ng.points.tasks.process_uploaded_file",
                obj,
                task_name=f"Uploading data: {obj.title}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key=request.session.session_key,
                type="upload", assign=True, notify=True
            )

            hooks.custom_admin_notification(
                request.session,
                "info",
                "Data upload for %s started. We will let you know when process is done." % (
                    obj.title
                )
            )
        return obj

    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = dict(show_save=False, show_save_and_continue=False)
        has_add_permission = self.has_add_permission
        self.has_add_permission = lambda __: False
        template_response = super().change_view(request, object_id, form_url, extra_context)
        self.has_add_permission = has_add_permission
        return template_response

@admin.register(models.ProfileCategory)
class ProfileCategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "category", "profile")
    list_filter = ("category", "profile",)

    fieldsets = (
        ("Database fields (can't change after being created)", {
            'fields': ('profile', 'category')
        }),
        ("Profile fields", {
          'fields': ('label', 'description',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("profile", "category",) + self.readonly_fields
        return self.readonly_fields
