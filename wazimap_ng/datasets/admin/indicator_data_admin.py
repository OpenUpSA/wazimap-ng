from django.contrib import admin
from django.contrib.postgres import fields
from django.urls import path

from django_json_widget.widgets import JSONEditorWidget

from .base_admin_model import DatasetBaseAdminModel
from .. import models
from .views.indicator_director_view import IndicatorDirectorAdminView

from wazimap_ng.general.admin import filters


@admin.register(models.IndicatorData)
class IndicatorDataAdmin(DatasetBaseAdminModel):
    add_form_template = "admin/indicatordata_change_list.html"

    def indicator__name(self, obj):
        return obj.indicator.name

    def parent(self, obj):
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

    class Media:
        js = ("/static/js/indicatordata-admin.js",)

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("geography", "indicator") + self.readonly_fields
        return self.readonly_fields
    
    def get_urls(self):
        urls = super(IndicatorDataAdmin, self).get_urls()
        my_urls = [
            path("upload/", IndicatorDirectorAdminView.as_view(), name="upload_indicator_director"),
        ]
        return my_urls + urls


