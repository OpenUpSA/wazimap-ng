import pandas as pd

from .. import models
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django_q.tasks import async_task

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.datasets import hooks
from .forms import CoordinateFileForm

@admin.register(models.CoordinateFile)
class CoordinateFileAdmin(BaseAdminModel):
    form = CoordinateFileForm
    fieldsets = [
        (None, { 'fields': ("profile", "theme",'name', 'document') } ),
    ]

    change_fieldsets = (
        ("Uploaded Dataset", {
            "fields": ("name", "document",)
        }),
        ("Task Details", {
            "fields": (
            	"get_status", "get_task_link", "get_errors",
            )
        }),
    )

    change_view_readonly_fields = (
       "name", "document", "get_status", "get_task_link",
       "get_errors",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.change_view_readonly_fields
        return self.readonly_fields


    def get_status(self, obj):
        if obj.id and obj.task:
                return "Processed" if obj.task.success else "Failed"
        return "In Queue"

    get_status.short_description = 'Status'

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
    get_task_link.short_description = 'Task Link'

    def get_errors(self, obj):
        if obj.task and not obj.task.success:
            result = obj.task.result
            if "CustomDataParsingExecption" in result:
                logdir = settings.MEDIA_ROOT + "/logs/points/"
                filename = "%s_%d_log.csv" % ("point_file", obj.id)
                download_url = settings.MEDIA_URL + "logs/points/"

                df = pd.read_csv(logdir+filename, header=None, sep=",", nrows=10, skiprows=1)
                error_list = df.values.tolist()

                result = render_to_string(
                    'custom/render_task_errors.html', { 'errors': error_list, 'download_url': download_url + filename}
                )

            return mark_safe(result)
        return "None"

    get_errors.short_description = 'Errors'


    def get_fieldsets(self, request, obj):
        fields = super().get_fieldsets(request, obj)
        if obj:
            fields = self.change_fieldsets
        return fields

    def save_model(self, request, obj, form, change):
        is_created = obj.pk == None and change == False
        super().save_model(request, obj, form, change)
        if is_created:
            profile = form.cleaned_data.get('profile')
            theme = form.cleaned_data.get('theme')
            async_task(
                "wazimap_ng.points.tasks.process_uploaded_file",
                obj, profile, theme, 
                task_name=f"Uploading data: {obj}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key=request.session.session_key,
                type="upload", assign=True, notify=True
            )

            hooks.custom_admin_notification(
                request.session,
                "info",
                "Data upload for %s started. We will let you know when process is done." % (
                    obj.name
                )
            )