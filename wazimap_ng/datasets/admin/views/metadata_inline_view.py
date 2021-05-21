from django.contrib import admin

from ... import models


class MetaDataInline(admin.StackedInline):
    model = models.MetaData
    fk_name = "dataset"

    verbose_name = ""
    verbose_name_plural = "Metadata"


    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "description":
            db_field.default = "Representation of data gathered from various sources"
        return super().formfield_for_dbfield(db_field, **kwargs)
