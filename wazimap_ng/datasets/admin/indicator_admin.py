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
from .. import widgets
from .base_admin_model import BaseAdminModel
from ...admin_utils import customTitledFilter

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

@admin.register(models.Indicator)
class IndicatorAdmin(BaseAdminModel):

    list_display = (
        "name", "dataset", "universe"
    )

    list_filter = (
        ("dataset", customTitledFilter("Dataset")),
    )

    form = IndicatorAdminForm
    fieldsets_add_view = [
        (None, { 'fields': ('dataset', ) } ),
    ]
    fieldsets = [
        (None, { 'fields': ('dataset','universe', 'groups', 'name', 'subindicators') } ),
    ]

    formfield_overrides = {
        fields.JSONField: {"widget": widgets.SortableWidget},
    }

    def get_related_fields_data(self, obj):
        return [{
            "name": "indicator data",
            "count": obj.indicatordata_set.count()
        }]

    def add_view(self, request, form_url='', extra_context=None):
        if request.POST.get("_saveasnew"):
            self.fieldsets = IndicatorAdmin.fieldsets
        else:
            self.fieldsets = IndicatorAdmin.fieldsets_add_view

        extra_context = extra_context or {}
        extra_context['show_save'] = False
        return admin.ModelAdmin.add_view(self, request, form_url, extra_context)

    def change_view(self, request, *args, **kwargs):
        self.fieldsets = IndicatorAdmin.fieldsets
        return admin.ModelAdmin.change_view(self, request, *args, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            to_add = ('dataset',)
            if obj.name:
                to_add = to_add + ("groups", "universe",)
            return self.readonly_fields + to_add
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        run_task = False

        if change:
            db_obj = models.Indicator.objects.get(id=obj.id)
            if not db_obj.name:
                run_task = True
        super().save_model(request, obj, form, change)
        if run_task:
            async_task(
                "wazimap_ng.datasets.tasks.indicator_data_extraction",
                obj,
                task_name=f"Data Extraction: {obj.name}",
                hook="wazimap_ng.datasets.hooks.notify_user",
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