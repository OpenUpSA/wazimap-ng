from django import forms
from django.core.exceptions import ValidationError
from django_json_widget.widgets import JSONEditorWidget

from wazimap_ng.general.widgets import VariableFilterWidget

from ... import models


class ProfileIndicatorAdminForm(forms.ModelForm):
    class Meta:
        model = models.ProfileIndicator
        fields = '__all__'
        widgets = {
            'indicator': VariableFilterWidget,
            'chart_configuration': JSONEditorWidget,

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # do not show any subcategories by default,
        # it should be loaded based on selected profile via JS
        self.fields['subcategory'].choices = [["", "-----------"]]

        # filter subcategories by profile if initial data provided
        if self.data.get('profile'):
            subcategories = models.IndicatorSubcategory.objects.filter(
                category__profile_id=self.data['profile']
            )
            self.fields['subcategory'].choices += [
                [obj.id, obj.name] for obj in subcategories
            ]



    def clean_subcategory(self):
        subcategory = self.cleaned_data['subcategory']
        profile = self.cleaned_data['profile']

        # do not allow to save subcategory which not related to the selected profile
        if subcategory.category.profile != profile:
            msg = f'This subcategory cannot be selected with {profile} profile.'
            raise ValidationError(msg)

        return subcategory
