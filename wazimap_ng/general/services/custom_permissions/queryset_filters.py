
from .. import permissions
from wazimap_ng.profile.models import Profile
from wazimap_ng.datasets.models import Dataset, Indicator


# Profile
def get_filters_for_profilehighlight(user):
	profiles = permissions.get_custom_queryset(user, Profile)
	indicators = Indicator.objects.filter(**get_filters_for_indicator(user))
	return {"profile__in": profiles, "indicator__in": indicators}

def get_filters_for_profileindicator(user):
	profiles = permissions.get_custom_queryset(user, Profile)
	indicators = Indicator.objects.filter(**get_filters_for_indicator(user))
	return {"profile__in": profiles, "indicator__in": indicators}

def get_filters_for_profilekeymetrics(user):
	profiles = permissions.get_custom_queryset(user, Profile)
	indicators = Indicator.objects.filter(**get_filters_for_indicator(user))
	return {"profile__in": profiles, "variable__in": indicators}

def get_filters_for_logo(user):
	return {"profile__in": permissions.get_custom_queryset(user, Profile)}

def get_filters_for_indicatorcategory(user):
	return {"profile__in": permissions.get_custom_queryset(user, Profile)}

def get_filters_for_indicatorsubcategory(user):
	return {"category__profile__in":permissions.get_custom_queryset(user, Profile)}


# Dataset
def get_filters_for_indicator(user):
	datasets = permissions.get_custom_queryset(user, Dataset)
	return {"dataset__in": datasets}

def get_filters_for_dataset(user):
	herarchies = permissions.get_custom_queryset(
		user, Profile
	).values_list("geography_hierarchy")
	return {"geography_hierarchy__in": herarchies}