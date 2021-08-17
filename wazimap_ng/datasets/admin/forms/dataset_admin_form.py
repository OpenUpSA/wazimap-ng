from django import forms

from wazimap_ng.general.services.permissions import get_user_group


class DatasetAdminForm(forms.ModelForm):
    import_dataset = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super(DatasetAdminForm, self).clean()

        profile = cleaned_data.get('profile', None)
        permission_type = cleaned_data.get('permission_type', None)

        if permission_type == 'private' and profile is None:
            raise forms.ValidationError('Profile should be set for private permissions.')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.id:
            profiles = self.fields["profile"].queryset

            user_group = get_user_group(self.current_user)

            filtered_profile = None
            if profiles.count() == 1:
                profile = profiles.first()
            elif user_group:
                filtered_profile = profiles.filter(
                    name__iexact=user_group.name
                ).first()

            if filtered_profile:
                self.fields["profile"].initial = filtered_profile