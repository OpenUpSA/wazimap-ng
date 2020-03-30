from django.contrib import admin

from ... import models

class InitialDataUploadAddView(admin.StackedInline):
    model = models.DatasetFile
    fk_name = "dataset"
    exclude = ("task", )

    verbose_name = ""
    verbose_name_plural = ""

    fieldsets = (
        ("Initial Data Upload - Use this form to upload file that will allow us to create dataset.", {
            "fields": ("document",)
        }),
    )
