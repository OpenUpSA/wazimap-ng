from django.contrib import admin
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

import pandas as pd

from ... import models

class InitialDataUploadChangeView(admin.StackedInline):
    model = models.DatasetFile
    fk_name = "dataset"
    exclude = ("task", )
    can_delete = False
    verbose_name = ""
    verbose_name_plural = ""

    fieldsets = (
        ("Uploaded Dataset", {
            "fields": ("document", )
        }),
        ("Task Details", {
            "fields": ("get_status", "get_task_link",)
        }),
    )

    error_and_warning_fieldset = ("Error & Warnings while data extraction", {
        "fields": ("get_warnings", "get_errors",)
    })

    readonly_fields = (
        "document", "get_status", "get_task_link", "get_warnings", "get_errors",
    )

    def get_status(self, obj):
        if obj.id:
            if obj.task:
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

    def get_warnings(self, obj):
        if obj.task:
            result = obj.task.result
            if obj.task.success and result["warning_log"]:
                download_url = result["warning_log"].replace("/app", "")
                result = render_to_string(
                    'custom/variable_task_warnings.html', {'download_url': download_url}
                )
                return mark_safe(result)
        return "-"

    get_warnings.short_description = 'Warnings'

    def get_errors(self, obj):
        if obj.task:
            result = obj.task.result
            if not obj.task.success:
                return obj.task.result
            elif result["error_log"]:
                download_url = result["error_log"].replace("/app", "")
                df = pd.read_csv(result["error_log"], header=None, sep=",", nrows=10, skiprows=1)
                error_list = df.values.tolist()
                result = render_to_string(
                    'custom/variable_task_errors.html', { 'errors': error_list,'download_url': download_url}
                )
                return mark_safe(result)
        return "None"

    get_errors.short_description = 'Errors'

    def get_fieldsets(self, request, obj):
        fields = super().get_fieldsets(request, obj)
        if obj.datasetfile.task:
            fields = fields + (self.error_and_warning_fieldset, )

        return fields
