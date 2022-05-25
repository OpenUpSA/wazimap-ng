from django import forms

from wazimap_ng.datasets.models import Licence
from wazimap_ng.general.models import MetaData
from wazimap_ng.general.admin.forms import HistoryAdminForm
from ... import models

from io import BytesIO
import pandas as pd

from django.core.exceptions import ValidationError


class CategoryAdminForm(HistoryAdminForm):
    source = forms.CharField(widget=forms.TextInput(attrs={'class': 'vTextField'}), required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField'}), required=False)
    licence = forms.ModelChoiceField(queryset=Licence.objects.all(), required=False)
    import_collection = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            if self.instance.metadata:
                metadata = self.instance.metadata
                self.fields["source"].initial = metadata.source
                self.fields["description"].initial = metadata.description
                self.fields["licence"].initial = metadata.licence

    def clean(self):
        cleaned_data = super(CategoryAdminForm, self).clean()
        document = cleaned_data.get('import_collection', None)
        required_headers = ["name", "longitude", "latitude"]
        if document is not None:
            headers = pd.read_csv(BytesIO(document.read()), nrows=1, dtype=str).columns.str.lower().str.strip()
            missing_headers = [
                h.capitalize() for h in list(set(required_headers) - set(headers))
            ]

            if missing_headers:
                missing_headers.sort()
                raise ValidationError(
                    f"Invalid File passed. We were not able to find Required header : {', '.join(missing_headers)}"
                )

    def save(self, commit=True):
        if self.has_changed():
            metadata = {
                key: self.cleaned_data.get(key) for key in [
                    "source", "description", "licence"
                ]
            }
            create_metadata = not self.instance.id or (self.instance.id and self.instance.metadata == None)

            if create_metadata:
                self.instance.metadata = MetaData.objects.create(**metadata)
            else:
                MetaData.objects.filter(id=self.instance.metadata.id).update(**metadata)
        return super().save(commit=commit)

    class Meta:
        model = models.Category
        fields = "__all__"
