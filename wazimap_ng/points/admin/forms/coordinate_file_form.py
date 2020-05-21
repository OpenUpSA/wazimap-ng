from django import forms

from ... import models
from wazimap_ng.profile.models import Profile
from wazimap_ng.general.services.permissions import get_custom_fk_queryset

class CoordinateFileForm(forms.ModelForm):
    profile = forms.ModelChoiceField(queryset=Profile.objects.none(), required=True)
    theme = forms.ModelChoiceField(queryset=models.Theme.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile"].queryset = get_custom_fk_queryset(
            self.current_user, Profile
        )
        self.fields["theme"].queryset = get_custom_fk_queryset(
            self.current_user, models.Theme
        )