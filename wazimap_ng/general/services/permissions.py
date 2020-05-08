from guardian.shortcuts import (
    get_group_perms, get_perms_for_model, get_groups_with_perms
)

from guardian.shortcuts import get_objects_for_user as guardian_objects_for_user

def has_dataset_permissions(user, obj, permission):
    if not hasattr(obj, "dataset"):
        return None

    dataset = obj.dataset
    is_delete_permission = "delete" in permission.lower()

    if dataset.permission_type == "public" and not is_delete_permission:
        return True

    return user.has_perm(permission, dataset)

def has_permission(user, obj, permission):
    if user.is_superuser:
        return True

    dataset_permissions = has_dataset_permissions(user, obj, permission)
    if dataset_permissions is not None:
        return dataset_permissions

    return user.has_perm(permission, obj)

def has_owner_permission(user, obj, permission):
    if user.is_superuser:
        return True

    return user.has_perm(permission, obj)

def get_objects_for_user(user, perm, model, queryset=None):
    queryset = queryset or model.objects.all()

    if (user.is_superuser):
        return queryset

    """
    Get Objects for a user according access type of object
    """
    model_name = model._meta.model_name
    if model_name not in ["profile", "dataset", "profilecategory", "category"]:
        return model.objects.none()

    app_label = model._meta.app_label
    codename = get_perms_for_model(model).filter(
        codename__contains=perm
    ).first().codename

    if not codename:
        return model.objects.none()

    queryset = queryset.exclude(**{"permission_type": "private"})
    queryset |= guardian_objects_for_user(
        user, f'{app_label}.{codename}', accept_global_perms=False
    )

    return queryset

# TODO Perhaps this function should move to the profile app instead
def get_user_profiles(user, permission="view", qs=None):
    from wazimap_ng.profile.models import Profile

    qs = qs or Profile.objects.all()

    return get_objects_for_user(user, permission, Profile, queryset=qs)

# TODO Perhaps this function should move to the points app instead
def get_user_categories(user, permission="view", qs=None):
    from wazimap_ng.points.models import Category

    qs = qs or Category.objects.all()
    if user.is_superuser:
        return qs

    profiles = get_user_profiles(user, permission)
    profile_ids = profiles.values_list("id", flat=True)
        
    qs = get_objects_for_user(user, permission, Category, qs)
    return qs.filter(theme__profile_id__in=profile_ids)

# TODO Perhaps this function should move to the points app instead
def get_user_themes(user, permission="view", qs=None):
    from wazimap_ng.points.models import Theme

    profiles = get_user_profiles(user)
    profile_ids = profiles.values_list("id", flat=True)

    return Theme.objects.filter(profile_id__in=profile_ids)
