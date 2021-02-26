import logging

from django.contrib import admin
from django.contrib.postgres import fields
from django.urls import path
from django.shortcuts import redirect

from django_json_widget.widgets import JSONEditorWidget
from django.template.response import TemplateResponse

from .base_admin_model import DatasetBaseAdminModel
from .. import models
from .forms import IndicatorDirectorForm

from wazimap_ng.general.admin import filters

logger = logging.getLogger(__name__)

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
            path("upload/", self.upload_indicator_director),
        ]
        return my_urls + urls

    def upload_indicator_director(self, request):

        if request.POST:
            indicator_director_file = request.POST.get("indicator_director_file", None)

            logger.debug(f"Indicator director file")
            #reader = csv.reader(csv_file)
            # Create Hero objects from passed in data
            # ...
           # self.message_user(request, "Your csv file has been imported")
            return redirect("/admin/datasets/indicatordata/")

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
            'title': "Upload JSON Indicator Director File",
            'add': False,
            'change': False,
            'original': "Upload Indicator",
            'form': IndicatorDirectorForm(),
        }

        return TemplateResponse(
            request, 
            "admin/indicatordata_upload_director.html", 
            context,
        )


