from django.contrib import admin

from ... import models


class MetaDataInline(admin.StackedInline):
    model = models.MetaData
    fk_name = "dataset"

    verbose_name = ""
    verbose_name_plural = "Metadata"