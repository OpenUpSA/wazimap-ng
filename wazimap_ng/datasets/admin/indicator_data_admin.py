from typing import Sequence

from django.contrib import admin
from django.contrib.postgres import fields
from django.http.request import HttpRequest
from django_json_widget.widgets import JSONEditorWidget

from wazimap_ng.datasets.models import Geography, IndicatorData
from wazimap_ng.general.admin import filters

from .. import models
from .base_admin_model import DatasetBaseAdminModel


@admin.register(models.IndicatorData)
class IndicatorDataAdmin(DatasetBaseAdminModel):

    def indicator__name(self, obj: IndicatorData) -> str:
        return obj.indicator.name

    def parent(self, obj: IndicatorData) -> Geography:
        return obj.geography.get_parent()

    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
    }

    fieldsets = (
        ("Database fields (can't change after being created)", {
            "fields": ("geography", "indicator")
        }),
        ("Data fields", {
            "fields": ("data",)
        })
    )

    list_display = (
        "indicator__name", "geography", "parent"
    )

    list_filter = (filters.IndicatorFilter,)

    search_fields = ["geography__name"]

    def get_readonly_fields(self, request: HttpRequest, obj: IndicatorData = None) -> Sequence:
        if obj:  # editing an existing object
            return ("geography", "indicator") + self.readonly_fields
        return self.readonly_fields
