import json
from django import forms

from wazimap_ng.general.services.permissions import get_user_group


class HistoryAdminForm(forms.ModelForm):
    change_reason_help = ("Explanation for the change")
    change_reason = forms.CharField(
        max_length=1024, help_text=change_reason_help, required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 100})
    )