import operator
from functools import reduce


from django import forms
from django.contrib import admin
from django.db.models import Q, CharField
from django.contrib.postgres import fields
from django.db.models.functions import Cast

from django_q.tasks import async_task

from .. import models
from .. import hooks
from .base_admin_model import DatasetBaseAdminModel
from wazimap_ng.general.services import permissions
from wazimap_ng.general.widgets import description

def get_source(indicator):
    if hasattr(indicator.dataset, "metadata"):
        return indicator.dataset.metadata.source
    return None 

class IndicatorAdminForm(forms.ModelForm):
    groups = forms.ChoiceField(required=True)
    class Meta:
        model = models.Indicator
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields
        if not self.instance.id:
            self.fields['groups'].choices = self.group_choices
            self.fields['universe'].queryset = self.universe_queryset

    def clean(self,*args,**kwargs):
        cleaned_data = super().clean(*args,**kwargs)
        cleaned_data['groups'] = [cleaned_data.get("groups")]
        return cleaned_data


class DatasetsWithPermissionFilter(admin.SimpleListFilter):
    title = 'Datasets'

    parameter_name = 'dataset_id'

    def lookups(self, request, model_admin):
        datasets = permissions.get_objects_for_user(request.user, models.Dataset)
        return [(d.id, d.name) for d in datasets]

    def queryset(self, request, queryset):
        dataset_id = self.value()

        if dataset_id is None:
            return queryset
        return queryset.filter(dataset__id=dataset_id)

@admin.register(models.Indicator)
class IndicatorAdmin(DatasetBaseAdminModel):

    list_display = (
        "name", "dataset", "universe", description("source", get_source)
    )

    list_filter = (
        DatasetsWithPermissionFilter, "dataset__metadata__source"
    )

    form = IndicatorAdminForm
    fieldsets = [
        (None, { 'fields': ('dataset', 'groups','universe', 'name',) } ),
    ]

    class Media:
        js = ("/static/js/jquery-ui.min.js", "/static/js/indicator-admin.js",)

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
        else:
            if not obj:
                dataset_id = request.POST.get('dataset', "")
                dataset = models.Dataset.objects.filter(id=dataset_id).first()
                groups = dataset.groups

                form.group_choices = [[group, group] for group in dataset.groups]
                condition = reduce(
                    operator.or_, [Q(as_string__icontains=group) for group in groups]
                )
                # form.universe_queryset = models.Universe.objects.annotate(
                #     as_string=Cast('filters', CharField())
                # ).filter(condition)
                form.universe_queryset = models.Universe.objects.annotate(
                    as_string=Cast('filters', CharField())
                )
        return form
