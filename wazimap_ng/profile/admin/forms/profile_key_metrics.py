from django import forms
from wazimap_ng.datasets.models import Indicator

class ProfileKeyMetricsForm(forms.ModelForm):
    MY_CHOICES = (
        (None, '-------------'),
    )

    subindicator = forms.ChoiceField(choices=MY_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'variable' in self.data:
            try:
                variable_id = int(self.data.get('variable'))
                self.fields['subindicator'].choices = [
                    [subindicator['id'], subindicator['label']] for subindicator in list(Indicator.objects.filter(id=variable_id).first().subindicators)
                ]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['subindicator'].choices = [
                [subindicator['id'], subindicator['label']] for subindicator in Indicator.objects.filter(id=self.instance.variable.pk).first().subindicators
            ]

            