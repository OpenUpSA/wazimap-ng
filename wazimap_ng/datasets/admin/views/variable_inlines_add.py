import operator
from functools import reduce

from django.contrib import admin
from django import forms
from django.db.models import Q, CharField
from django.db.models.functions import Cast

from ... import models

class VariableInlinesAdminForm(forms.ModelForm):
    groups = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = models.Indicator
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            dataset = self.fields["dataset"].queryset.first()
            choices = [[group, group] for group in dataset.groups]
            if "groups" in self.fields:
                self.fields['groups'].choices = choices

            if "universe" in self.fields:
                if not dataset.groups:
                    self.fields['universe'].queryset = models.Universe.objects.none()
                else:
                    condition = reduce(
                        operator.or_, [Q(as_string__icontains=group) for group in dataset.groups]
                    )
                    self.fields['universe'].queryset = models.Universe.objects.annotate(
                        as_string=Cast('filters', CharField())
                    ).filter(condition)


class VariableInlinesAddView(admin.StackedInline):
    model = models.Indicator
    fk_name= "dataset"
    form = VariableInlinesAdminForm
    extra = 0
    verbose_name_plural = "Add New Variable"
    exclude = ("subindicators", )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = request.META['PATH_INFO'].rstrip('/').split('/')[-2]
        if db_field.name == 'dataset' and obj_id.isdigit():
            if obj_id:
                kwargs['queryset'] = models.Dataset.objects.filter(id=obj_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_view_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
