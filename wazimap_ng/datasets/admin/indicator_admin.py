import operator
from functools import reduce

from django.contrib import admin
from django.db.models import Q, CharField
from django.contrib.postgres import fields
from django.db.models.functions import Cast
from django.db import transaction

from django_q.tasks import async_task

from .. import models
from .. import hooks
from .forms import IndicatorAdminForm
from .base_admin_model import DatasetBaseAdminModel
from wazimap_ng.general.services import permissions
from wazimap_ng.general.widgets import description
from wazimap_ng.general.admin import filters


def get_source(indicator):
    if hasattr(indicator.dataset, "metadata"):
        return indicator.dataset.metadata.source
    return None


# Custom Filters
class PermissionTypeFilter(filters.DatasetFilter):
    title = "Permission Type"
    model_class = models.Indicator
    parameter_name = "dataset__permission_type"

    def lookups(self, request, model_admin):
        return [("private", "Mine"), ("public", "Public")]

class IndicatorProfileFilter(filters.ProfileFilter):
    parameter_name = 'dataset__profile'

class IndicatorGeographyHierarchyFilter(filters.GeographyHierarchyFilter):
    parameter_name = 'dataset__geography_hierarchy_id'


@admin.register(models.Indicator)
class IndicatorAdmin(DatasetBaseAdminModel):

    list_display = (
        "name", "dataset", "universe", description("source", get_source)
    )

    list_filter = (
        PermissionTypeFilter, IndicatorProfileFilter,
        IndicatorGeographyHierarchyFilter
    )

    form = IndicatorAdminForm
    fieldsets = [
        (None, { 'fields': ('dataset', 'groups','universe', 'name',) } ),
    ]

    autocomplete_fields = ("dataset", )
    search_fields = ("name", )

    class Media:
        js = ("/static/js/indicator-admin.js",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            to_add = ('dataset',"groups", "universe",)
            return self.readonly_fields + to_add
        return self.readonly_fields

    def get_related_fields_data(self, obj):
        return [{
            "name": "indicator data",
            "count": obj.indicatordata_set.count()
        }]

    def save_model(self, request, obj, form, change):
        """
        During Step 1, no background tasks are run because only the Dataset is available.
        """
        run_task = False if change else True
        run_task = True

        with transaction.atomic():
            super().save_model(request, obj, form, change)
        
        if run_task:
            task = async_task(
                "wazimap_ng.datasets.tasks.indicator_data_extraction",
                obj,
                task_name=f"Data Extraction: {obj.name}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key=request.session.session_key,
                type="data_extraction", assign=False, notify=True
            )
            hooks.add_to_task_list(request.session, task)
            hooks.custom_admin_notification(
                request.session,
                "info",
                "Process of Data extraction started for %s. We will let you know when process is done." % (
                    obj.name
                )
            )
        return obj

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if request.method == "GET":
            form.group_choices = [["", "-----------"]]
            form.universe_queryset = models.Universe.objects.none()
            form.dataset_queryset = models.Dataset.objects.none()
        else:
            if not obj:
                dataset_id = request.POST.get('dataset', "")
                dataset = models.Dataset.objects.filter(id=dataset_id).first()
                groups = dataset.groups

                form.group_choices = [[group, group] for group in dataset.groups]
                # condition = reduce(
                #     operator.or_, [Q(as_string__icontains=group) for group in groups]
                # )
                # form.universe_queryset = models.Universe.objects.annotate(
                #     as_string=Cast('filters', CharField())
                # ).filter(condition)
                form.universe_queryset = models.Universe.objects.annotate(
                    as_string=Cast('filters', CharField())
                )
                form.dataset_queryset = models.Dataset.objects.exclude(permission_type='restricted')
        return form
