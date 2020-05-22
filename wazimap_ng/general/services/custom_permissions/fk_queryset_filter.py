from django.db import models

from .. import permissions
from wazimap_ng.profile.models import Profile
from wazimap_ng.points.models import Category
from wazimap_ng.datasets.models import Dataset


class CustomFKQuerySet(models.QuerySet):

	def get_category_queryset(self, user):
		profiles = permissions.get_objects_for_user(user, Profile)

		return permissions.get_objects_for_user(
			user, Category, queryset=self.filter(profile__in=profiles)
		)

	def get_profile_queryset(self, user):
		return permissions.get_objects_for_user(
			user, Profile, include_public=False
		)

	def get_theme_queryset(self, user):
		profiles = permissions.get_objects_for_user(
			user, Profile, include_public=False
		)
		return self.filter(profile__in=profiles)

	def get_indicatorcategory_queryset(self, user):
		profiles = permissions.get_objects_for_user(
			user, Profile, include_public=False
		)
		return self.filter(profile__in=profiles)

	def get_indicatorsubcategory_queryset(self, user):
		profiles = permissions.get_objects_for_user(
			user, Profile, include_public=False
		)
		return self.filter(category__profile__in=profiles)

	def get_indicator_queryset(self, user):
		profiles = permissions.get_objects_for_user(user, Profile)
		datasets = permissions.get_objects_for_user(
			user, Dataset, queryset=Dataset.objects.filter(
				profile__in=profiles
			)
		)
		return self.filter(dataset__in=datasets)

	def get_geographyhierarchy_queryset(self, user):
		ids = permissions.get_objects_for_user(
			user, Profile, include_public=False
		).values_list("geography_hierarchy_id", flat=True)

		return self.filter(id__in=ids)

	def get_dataset_queryset(self, user):
		profiles = permissions.get_objects_for_user(user, Profile)
		return permissions.get_objects_for_user(
			user, Dataset, queryset=Dataset.objects.filter(profile__in=profiles)
		)