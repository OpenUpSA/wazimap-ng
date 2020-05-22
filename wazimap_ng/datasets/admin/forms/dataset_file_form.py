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
        profiles =  get_custom_fk_queryset(self.current_user, Profile)
        heirarchies = get_custom_fk_queryset(self.current_user, models.GeographyHierarchy)

        self.fields["profile"].queryset = profiles
        self.fields["geography_hierarchy"].queryset = heirarchies

        if profiles.count() == 1:
            profile = profiles.first()
            self.fields["profile"].initial = profile

            for heirarchy in heirarchies:
                hp = heirarchy.profile_set.all()
                if hp.count() == 1 and hp.first() == profile:
                    self.fields["geography_hierarchy"].initial = heirarchy
                    self.fields["geography_hierarchy"].widget.attrs['disabled'] = True