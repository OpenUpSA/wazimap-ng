from django import forms

from wazimap_ng.datasets.models import Licence
from wazimap_ng.general.models import MetaData
from wazimap_ng.points.models import Category


class CategoryAdminForm(forms.ModelForm):
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

    def save(self, commit: bool = True):
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
        model = Category
        fields = "__all__"
