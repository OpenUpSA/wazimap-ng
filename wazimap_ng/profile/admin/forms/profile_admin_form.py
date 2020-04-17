from django import forms

from ... import models
from guardian.admin import GuardedModelAdmin

class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        widgets = {
          'profile_type': forms.RadioSelect,
        }
        fields = '__all__'