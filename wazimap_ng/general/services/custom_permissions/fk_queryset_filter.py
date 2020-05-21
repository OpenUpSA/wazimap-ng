from .. import permissions
from wazimap_ng.profile.models import Profile


def get_filters_for_geographyhierarchy(user):
	hierarchies = permissions.get_custom_queryset(
		user, Profile
	).values_list("geography_hierarchy_id", flat=True)
	return {"id__in": hierarchies}