from django import forms

from ... import models
from wazimap_ng.profile.models import Profile
from wazimap_ng.general.services.permissions import get_custom_fk_queryset

class DatasetFileForm(forms.ModelForm):
    profile = forms.ModelChoiceField(queryset=Profile.objects.none(), required=True)
    geography_hierarchy = forms.ModelChoiceField(
        queryset=models.GeographyHierarchy.objects.none(), required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile"].queryset = get_custom_fk_queryset(
            self.current_user, Profile
        )
        self.fields["geography_hierarchy"].queryset = get_custom_fk_queryset(
            self.current_user, models.GeographyHierarchy
        )