from django import forms


class DatasetAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.id:
            profiles = self.fields["profile"].queryset
            heirarchies = self.fields["geography_hierarchy"].queryset
            if profiles.count() == 1:
                profile = profiles.first()
                self.fields["profile"].initial = profile

                for heirarchy in heirarchies:
                    hp = heirarchy.profile_set.all()
                    if hp.count() == 1 and hp.first() == profile:
                        self.fields["geography_hierarchy"].initial = heirarchy
                        self.fields["geography_hierarchy"].widget.attrs['disabled'] = True