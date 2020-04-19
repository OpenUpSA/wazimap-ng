from django import forms

from wazimap_ng.datasets.models import Indicator

class ProfileHighlightForm(forms.ModelForm):
    MY_CHOICES = (
        (None, '-------------'),
    )

    subindicator = forms.ChoiceField(choices=MY_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_indicators = Indicator.objects.all()

        if 'indicator' in self.data:
            try:
                variable_id = int(self.data.get('indicator'))
                self.fields['subindicator'].choices = [
                    [subindicator["id"], subindicator["label"]] 
                    for subindicator in all_indicators.filter(id=variable_id).first().subindicators
                ]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['subindicator'].choices = [
                [subindicator["id"], subindicator["label"]]
                for subindicator in all_indicators.filter(id=self.instance.indicator.pk).first().subindicators
            ]