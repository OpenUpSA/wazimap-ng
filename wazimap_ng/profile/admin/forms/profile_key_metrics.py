import logging

from django import forms

from ... import models
from wazimap_ng.datasets.models import Indicator
from wazimap_ng.general.widgets import VariableFilterWidget
from wazimap_ng.general.admin.forms import HistoryAdminForm

logger = logging.getLogger(__name__)

class ProfileKeyMetricsForm(HistoryAdminForm):
    MY_CHOICES = (
        (None, '-------------'),
    )

    subindicator = forms.ChoiceField(choices=MY_CHOICES, required=False)

    class Meta:
        model = models.ProfileKeyMetrics
        fields = "__all__"
        widgets = {
            "variable": VariableFilterWidget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_saving_new_item = "variable" in self.data
        is_editing_item = self.instance.pk is not None

        self.fields['variable'].queryset = Indicator.objects.filter(
            dataset__content_type="quantitative"
        )

        try:
            if is_saving_new_item:
                variable_id = int(self.data.get('variable'))
                indicator = Indicator.objects.get(pk=variable_id)
            elif is_editing_item:
                indicator = Indicator.objects.get(pk=self.instance.variable.pk)
            else:
                logger.warning("Unsure how to handle creating ProfileHighlightForm")
                return
            self.fields['subindicator'].choices = [(idx, s) for (idx, s) in enumerate(indicator.subindicators)]
        except Exception as e:
            logger.exception(e)
