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
from .base_admin_model import BaseAdminModel
from ...admin_utils import customTitledFilter, SortableWidget
from wazimap_ng.general.services import permissions

class IndicatorAdminForm(forms.ModelForm):
    groups = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = models.Indicator
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            choices = [[group, group] for group in self.instance.dataset.groups]

            if "groups" in self.fields:
                self.fields['groups'].choices = choices
                self.fields['groups'].initial = self.instance.groups

            if "universe" in self.fields:
                if not self.instance.dataset.groups:
                    self.fields['universe'].queryset = models.Universe.objects.none()
                else:
                    condition = reduce(
                        operator.or_, [Q(as_string__icontains=group) for group in self.instance.dataset.groups]
                    )
                    self.fields['universe'].queryset = models.Universe.objects.annotate(
                        as_string=Cast('filters', CharField())
                    ).filter(condition)

    def clean_subindicators(self):
        values = self.instance.subindicators
        order = self.cleaned_data['subindicators']
        return [values[i] for i in order] if order else values

class DatasetsWithPermissionFilter(admin.SimpleListFilter):
    title = 'Datasets'

    parameter_name = 'dataset_id'

    def lookups(self, request, model_admin):
        datasets = permissions.get_objects_for_user(request.user, 'view', models.Dataset)
        return [(d.id, d.name) for d in datasets]

    def queryset(self, request, queryset):
        dataset_id = self.value()

        if dataset_id is None:
            return queryset
        return queryset.filter(dataset__id=dataset_id)

@admin.register(models.Indicator)
class IndicatorAdmin(BaseAdminModel):
    """
    This Admin creates an Indicator in two steps.
    Step 1: Select the Dataset
    Step 2: Complete the indicator by selecting groups, providing a label, etc.

    TODO may want to rather do this with javascript
    """

    list_display = (
        "name", "dataset", "universe"
    )

    list_filter = (
        DatasetsWithPermissionFilter,
    )

    form = IndicatorAdminForm
    step1_fieldsets = [
        (None, { 'fields': ('dataset', ) } ),
    ]

    step2_fieldsets = [
        (None, { 'fields': ('dataset','universe', 'groups', 'name', 'subindicators') } ),
    ]

    formfield_overrides = {
        fields.JSONField: {"widget": SortableWidget},
    }

    def add_view(self, request, form_url='', extra_context=None):
        if request.POST.get("_saveasnew"):
            self.fieldsets = IndicatorAdmin.step2_fieldsets
        else:
            self.fieldsets = IndicatorAdmin.step1_fieldsets

        extra_context = extra_context or {}
        extra_context['show_save'] = False

        # TODO why is this not using super()?
        return admin.ModelAdmin.add_view(self, request, form_url, extra_context)

    def change_view(self, request, *args, **kwargs):
        self.fieldsets = IndicatorAdmin.step2_fieldsets
        # TODO why is this not using super()?
        return admin.ModelAdmin.change_view(self, request, *args, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            to_add = ('dataset',)
            if obj.name:
                to_add = to_add + ("groups", "universe",)
            return self.readonly_fields + to_add
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "dataset":
            qs = permissions.get_objects_for_user(request.user, 'view', models.Dataset)
            kwargs["queryset"] = qs.filter(datasetfile__task__success=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        During Step 1, no background tasks are run because only the Dataset is available.
        """
        run_task = False

        if change:
            db_obj = models.Indicator.objects.get(id=obj.id)
            is_first_save = not db_obj.name
            
            if is_first_save:
                run_task = True

        super().save_model(request, obj, form, change)
        if run_task:
            async_task(
                "wazimap_ng.datasets.tasks.indicator_data_extraction",
                obj,
                task_name=f"Data Extraction: {obj.name}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key=request.session.session_key
            )
            hooks.custom_admin_notification(
                request.session,
                "info",
                "Process of Data extraction started for %s. We will let you know when process is done." % (
                    obj.name
                )
            )

        if not change:
            hooks.custom_admin_notification(
                request.session,
                "warning",
                "Please make sure you get data right before saving as fields : groups, dataset & universe will be set as non editable"
            )
        return obj

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        datasets = permissions.get_objects_for_user(request.user, 'view', models.Dataset)
        return qs.filter(dataset__in=datasets)