from django.db.models import Q
from wazimap_ng.datasets.models import Indicator


def filter_indicators_by_profile(profile_id, queryset=None):
    if not queryset:
        queryset = Indicator.objects.all()
    if profile_id:
        queryset = queryset.filter(
            Q(dataset__permission_type="public")
            | Q(dataset__permission_type="private", dataset__profile_id=profile_id)
        )
    return queryset
