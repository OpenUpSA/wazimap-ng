from django import forms
from django.contrib.auth.models import Group

from ... import models
from wazimap_ng.admin_utils import GroupPermissionWidget
from guardian.admin import GuardedModelAdmin


class ProfileAdminForm(forms.ModelForm):
	groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, widget=GroupPermissionWidget)

	

	class Meta:
		model = models.Profile
		widgets = {
			'profile_type': forms.RadioSelect,
		}
		fields = '__all__'


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["groups"].widget.current_user = self.current_user
		self.fields["groups"].widget.target = self.instance