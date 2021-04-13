from django import forms

from wazimap_ng.general.services.permissions import get_user_group


class DatasetAdminForm(forms.ModelForm):
    import_dataset = forms.FileField(required=False)

    def clean_profile(self):
        cleaned_data = super(DatasetAdminForm, self).clean()
        if cleaned_data['profile'] is None:
            raise forms.ValidationError('Profile is not set.')
        return cleaned_data['profile']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.id:
            profiles = self.fields["profile"].queryset
            hierarchies = self.fields["geography_hierarchy"].queryset

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

                for hierarchy in hierarchies:
                    hp = hierarchy.profile_set.all()
                    if hp.count() == 1 and hp.first() == filtered_profile:
                        self.fields["geography_hierarchy"].initial = hierarchy