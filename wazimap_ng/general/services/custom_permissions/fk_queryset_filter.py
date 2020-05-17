from .. import permissions
from wazimap_ng.profile.models import Profile

def get_filters_for_dataset(user):
	return {"datasetfile__task__success": True}

def get_filters_for_category(user):
	return {"coordinatefile__task__success": True}

def get_filters_for_geographyhierarchy(user):
	hierarchies = permissions.get_custom_queryset(
		user, Profile
	).values_list("geography_hierarchy_id", flat=True)
	return {"id__in": hierarchies}