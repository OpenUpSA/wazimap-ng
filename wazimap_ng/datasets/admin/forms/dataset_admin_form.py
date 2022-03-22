from django import forms

from wazimap_ng.general.services.permissions import get_user_groups
from wazimap_ng.general.admin.forms import HistoryAdminForm

from wazimap_ng.datasets.models import Version
from wazimap_ng.profile.models import Profile

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

        if "profile" in self.fields:
            self.fields['profile'].required = True
            profiles = self.fields["profile"].queryset
            versions = Version.objects.none()
            initial_profile = None

            if self.data:
                profile_id = self.data.get("profile", None)
                version = self.data.get("version", None)
                if profile_id:
                    initial_profile = profiles.filter(id=profile_id).first()
                    versions = self.get_versions(initial_profile)
            elif self.instance.id:
                initial_profile = self.instance.profile
                versions = self.get_versions(initial_profile)
            else:
                if not self.current_user.is_superuser:
                    user_groups = get_user_groups(self.current_user)
                    if user_groups:
                        profiles = profiles.filter(
                            name__in=user_groups.values_list("name", flat=True)
                        )
                if profiles.count() == 1:
                    initial_profile = profiles.first()
                    versions = self.get_versions(initial_profile)

            self.fields["profile"].queryset = profiles
            self.fields["version"].queryset = versions
            self.fields["profile"].initial = initial_profile
            if versions.count() == 1:
                self.fields["version"].initial = versions.first()
