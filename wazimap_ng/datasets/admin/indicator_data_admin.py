import logging
import json

from django.contrib import admin
from django.contrib.postgres import fields
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django_json_widget.widgets import JSONEditorWidget
from django.template.response import TemplateResponse

from django_q.tasks import async_task

from .base_admin_model import DatasetBaseAdminModel
from .. import hooks, models
from .forms import IndicatorDirectorForm

from wazimap_ng.general.admin import filters

logger = logging.getLogger(__name__)

@admin.register(models.IndicatorData)
class IndicatorDataAdmin(DatasetBaseAdminModel):
    add_form_template = "admin/indicatordata_change_form.html"

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
        css = {
             'all': ('/static/css/admin-custom.css',)
        }

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

    @login_required
    def upload_indicator_director(self, request):
        if request.method == 'POST':
            form = IndicatorDirectorForm(request.POST, request.FILES)
            if form.is_valid():
                indicator_director = request.FILES["indicator_director"]
                dataset = form.cleaned_data["dataset"]
                logger.debug(f" Uploaded Indicator director file: {indicator_director}")

                with open('/tmp/indicator_director.json', 'wb+') as f:
                    for chunk in indicator_director.chunks():
                        f.write(chunk)

                indicator_director.close()

                with open('/tmp/indicator_director.json', 'r') as z:
                    indicator_director_json = json.load(z)
                        
                #task to process director file comes here
                if indicator_director_json:
                    logger.debug(f"""Starting async task: 
                        Task name: wazimap_ng.datasets.tasks.process_indicator_data_director
                        Hook: wazimap_ng.datasets.hooks.process_task_info,
                        key: {request.session.session_key},
                        type: indicator_director,
                        assign: True,
                        notify: True
                    """)
                    
                    task = async_task(
                        "wazimap_ng.datasets.tasks.process_indicator_data_director",
                        indicator_director_json, dataset,
                        task_name=f"Creating Indicator data: {dataset}",
                        hook="wazimap_ng.datasets.hooks.process_task_info",
                        key=request.session.session_key,
                        type="indicator_director", assign=False, notify=True
                    )
                    hooks.add_to_task_list(request.session, task)
                    hooks.custom_admin_notification(
                        request.session,
                        "info",
                        "Indicator data creation for dataset %s started. We will let you know when process is done." % (
                            dataset
                        )
                    )
                return HttpResponseRedirect("/admin/datasets/indicatordata/")

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

