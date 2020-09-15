import logging

from django import forms

from ... import models
from wazimap_ng.datasets.models import Indicator
from wazimap_ng.general.widgets import VariableFilterWidget

logger = logging.getLogger(__name__)


class ProfileHighlightForm(forms.ModelForm):
    MY_CHOICES = (
        (None, '-------------'),
    )

    subindicator = forms.ChoiceField(choices=MY_CHOICES, required=False)

    class Meta:
        model = models.ProfileHighlight
        fields = "__all__"
        widgets = {
            'indicator': VariableFilterWidget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_saving_new_item = "indicator" in self.data
        is_editing_item = self.instance.pk is not None

        try:
            if is_saving_new_item:
                variable_id = int(self.data.get('indicator'))
                indicator = Indicator.objects.get(pk=variable_id)
            elif is_editing_item:
                indicator = Indicator.objects.get(pk=self.instance.indicator.pk)
            else:
                logger.warn("Unsure how to handle creating ProfileHighlightForm")
                return
            self.fields['subindicator'].choices = [(idx, s) for (idx, s) in enumerate(indicator.subindicators)]
        except (ValueError, TypeError) as e:
            logger.exception(e)
