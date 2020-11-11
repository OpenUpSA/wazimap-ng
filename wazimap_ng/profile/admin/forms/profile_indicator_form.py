from django import forms

from wazimap_ng.general.widgets import VariableFilterWidget
from django_json_widget.widgets import JSONEditorWidget

from ...models import IndicatorSubcategory, ProfileIndicator


class ProfileIndicatorAdminForm(forms.ModelForm):
    class Meta:
        model = ProfileIndicator
        fields = '__all__'
        widgets = {
            'indicator': VariableFilterWidget,
            'chart_configuration': JSONEditorWidget,

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # do not load any subcategories by default,
        # it should be loaded based on selected profile via JS
        self.fields['subcategory'].queryset = IndicatorSubcategory.objects.none()
