from django import forms

from wazimap_ng.general.services.permissions import get_user_group
from wazimap_ng.general.admin.forms import HistoryAdminForm

from wazimap_ng.datasets.models import Version

class DatasetAdminForm(HistoryAdminForm):
    import_dataset = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super(DatasetAdminForm, self).clean()

        profile = cleaned_data.get('profile', None)
        version = cleaned_data.get('version', None)

        if profile and version:
            versions = self.get_versions(profile)
            if version not in versions:
                raise forms.ValidationError(
                    f"Version {version} not valid for profile {profile}"
                )
        return cleaned_data

    def get_versions(self, profile):
        version_names = profile.geography_hierarchy.get_version_names
        return Version.objects.filter(name__in=version_names)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['profile'].required = True
        profiles = self.fields["profile"].queryset
        if not self.instance.id:
            user_group = get_user_group(self.current_user)
            filtered_profile = None
            filtered_versions = None

            if profiles.count() == 1:
                filtered_profile = profiles.first()
            elif user_group:
                filtered_profile = profiles.filter(
                    name__iexact=user_group.name
                ).first()

            if filtered_profile:
                filtered_versions = self.get_versions(filtered_profile)
                self.fields["profile"].initial = filtered_profile

            if filtered_versions:
                self.fields["version"].queryset = filtered_versions
                if filtered_versions.count() == 1:
                    self.fields["version"].initial = filtered_versions.first()
            else:
                self.fields["version"].queryset = Version.objects.none()
        else:
            profile = self.instance.profile
            if self.data:
                profile_id = self.data.get("profile", None)
                if profile_id:
                    profile = profiles.filter(id=profile_id).first()
            if profile:
                self.fields["version"].queryset = self.get_versions(profile)
