import logging
from datetime import datetime

from django.core.cache import cache
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import Http404
from django.views.decorators.cache import cache_control
from django.views.decorators.vary import vary_on_headers

from wazimap_ng.datasets.models import Group, Geography, DatasetData, GeographyHierarchy
from wazimap_ng.points.models import Location, Category, ProfileCategory
from wazimap_ng.profile.models import ProfileIndicator, ProfileHighlight, IndicatorCategory, IndicatorSubcategory, \
    ProfileKeyMetrics, Profile, Indicator
from wazimap_ng.profile.services import authentication

logger = logging.getLogger(__name__)

profile_key = "etag-Profile-%s"
location_key = "etag-Location-profile-%s-%s"
theme_key = "etag-Theme-profile-%s-%s"
location_theme_key = "etag-Location-Theme-%s"


def check_has_permission(request, profile_id):
    try:
        profile = Profile.objects.get(pk=profile_id)
        has_permission = authentication.has_permission(request.user, profile)
        if has_permission:
            return True
        return False
    except Profile.DoesNotExist:
        raise Http404


def last_modified(request, profile_id, key):
    if check_has_permission(request, profile_id):
        _last_modified = datetime(year=1970, month=1, day=1)
        c = cache.get(key)

        if c is not None:
            return c
        else:
            cache.set(key, datetime.now())
    else:
        _last_modified = datetime.now()
    return _last_modified


def etag_profile_updated(request, profile_id, geography_code):
    last_modified = last_modified_profile_updated(request, profile_id, geography_code)
    return str(last_modified)


def last_modified_profile_updated(request, profile_id, geography_code):
    key = profile_key % profile_id
    return last_modified(request, profile_id, key)


def etag_point_updated(request, profile_id, profile_category_id=None, theme_id=None, geography_code=None):
    last_modified = last_modified_point_updated(request, profile_id, profile_category_id, theme_id, geography_code)
    return str(last_modified)


def last_modified_point_updated(request, profile_id, profile_category_id=None, theme_id=None, geography_code=None):
    if profile_category_id is not None:
        key = location_key % (profile_id, profile_category_id)
    elif theme_id is not None:
        key = theme_key % (profile_id, theme_id)
    else:
        return None

    if geography_code is not None:
        key = f"{key}_{geography_code}"

    return last_modified(request, profile_id, key)


########### Signals #################
def update_profile_cache(profile):
    logger.info(f"Updating profile cache: {profile}")
    key = profile_key % profile.id
    cache.set(key, datetime.now())


def update_point_cache(profile, category):
    key1 = location_key % (profile.id, category.id)

    logger.debug(f"Set cache key (category): {key1}")
    cache.set(key1, datetime.now())


@receiver(post_delete, sender=ProfileIndicator)
@receiver(post_save, sender=ProfileIndicator)
def profile_indicator_updated(sender, instance, **kwargs):
    update_profile_cache(instance.profile)


@receiver(post_delete, sender=ProfileHighlight)
@receiver(post_save, sender=ProfileHighlight)
def profile_highlight_updated(sender, instance, **kwargs):
    update_profile_cache(instance.profile)


@receiver(post_delete, sender=IndicatorCategory)
@receiver(post_save, sender=IndicatorCategory)
def profile_category_updated(sender, instance, **kwargs):
    update_profile_cache(instance.profile)


@receiver(post_delete, sender=IndicatorSubcategory)
@receiver(post_save, sender=IndicatorSubcategory)
def profile_subcategory_updated(sender, instance, **kwargs):
    update_profile_cache(instance.category.profile)


@receiver(post_delete, sender=ProfileKeyMetrics)
@receiver(post_save, sender=ProfileKeyMetrics)
def profile_keymetrics_updated(sender, instance, **kwargs):
    update_profile_cache(instance.profile)


@receiver(post_delete, sender=Profile)
@receiver(post_save, sender=Profile)
def profile_updated(sender, instance, **kwargs):
    update_profile_cache(instance)


@receiver(post_delete, sender=Group)
@receiver(post_save, sender=Group)
def subindicator_group_update(sender, instance, **kwargs):
    indicator_ids = instance.dataset.indicator_set.values_list("id", flat=True)
    profiles_to_invalidate_cache = Profile.objects.filter(
        Q(id=instance.dataset.profile_id)
        | Q(profileindicator__indicator_id__in=indicator_ids)
        | Q(profilekeymetrics__variable_id__in=indicator_ids)
        | Q(profilehighlight__indicator_id__in=indicator_ids)
    ).distinct()
    for profile_obj in profiles_to_invalidate_cache:
        update_profile_cache(profile_obj)


@receiver(post_delete, sender=Location)
@receiver(post_save, sender=Location)
def point_updated_location(sender, instance, **kwargs):
    for pc in instance.category.profilecategory_set.all():
        update_point_cache(pc.profile, pc)
        update_profile_cache(pc.profile)


@receiver(post_delete, sender=Category)
@receiver(post_save, sender=Category)
def point_updated_category(sender, instance, **kwargs):
    profile_categoies = instance.profilecategory_set.all()
    for pc in profile_categoies:
        update_point_cache(pc.profile, pc)
        update_profile_cache(pc.profile)


@receiver(post_delete, sender=ProfileCategory)
@receiver(post_save, sender=ProfileCategory)
def point_updated_profile_category(sender, instance, **kwargs):
    update_point_cache(instance.profile, instance)
    update_profile_cache(instance.profile)


@receiver(post_delete, sender=Indicator)
@receiver(post_save, sender=Indicator)
def indicator_updated(sender, instance, **kwargs):
    indicator_id = instance.id
    profiles_to_invalidate_cache = Profile.objects.filter(
        Q(profileindicator__indicator_id=indicator_id)
        | Q(profilekeymetrics__variable_id=indicator_id)
        | Q(profilehighlight__indicator_id=indicator_id)
    ).distinct()
    for profile_obj in profiles_to_invalidate_cache:
        update_profile_cache(profile_obj)


@receiver(post_delete, sender=Geography)
@receiver(post_save, sender=Geography)
def geography_updated(sender, instance, **kwargs):

    # dataset data objs
    dataset_data_profile_ids = list(instance.datasetdata_set.values_list(
        "dataset__profile", flat=True
    ).order_by("dataset__profile").distinct())

    # indicator data objs
    indicator_data_profile_ids = list(instance.indicatordata_set.values_list(
        "indicator__dataset__profile", flat=True
    ).order_by("indicator__dataset__profile").distinct())

    # Get hierarchy profile linked to
    hierarchy_profile_ids = list(instance.geographyhierarchy_set.values_list(
        "profile", flat=True
    ).order_by("profile").distinct())

    profile_ids = set(dataset_data_profile_ids + indicator_data_profile_ids + hierarchy_profile_ids)
    for profile in Profile.objects.filter(id__in=set(profile_ids)):
        update_profile_cache(profile)


@receiver(post_delete, sender=GeographyHierarchy)
@receiver(post_save, sender=GeographyHierarchy)
def geography_hierarchy_updated(sender, instance, **kwargs):
    for profile in instance.profile_set.all():
        update_profile_cache(profile)


def cache_headers(func):
    return vary_on_headers("Authorization")(cache_control(max_age=0, public=True, must_revalidate=True)(func))


def cache_decorator(key, expiry=60 * 60 * 24 * 365):
    def clean(s):
        return str(s).replace(" ", "-").lower().strip()

    def _cache_decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = key
            if len(args) > 0:
                cache_key += "-".join(clean(el) for el in args)

            if len(kwargs) > 0:
                cache_key += "-".join(f"{k}-{v}" for k, v in kwargs.items())

            cached_obj = cache.get(cache_key)
            if cached_obj is not None:
                return cached_obj

            obj = func(*args, **kwargs)
            cache.set(cache_key, obj, expiry)
            return obj

        return wrapper

    return _cache_decorator
