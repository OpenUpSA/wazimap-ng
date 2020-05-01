from guardian.shortcuts import (
    get_group_perms, get_perms_for_model, get_groups_with_perms
)

from guardian.shortcuts import get_objects_for_user as guardian_objects_for_user

def get_user_groups_with_permission_on_object(obj, user):
    user_groups = user.groups.all()
    groups_with_permission = get_groups_with_perms(obj)

    groups = [g for g in user_groups if g in groups_with_permission]
    return groups

def get_user_groups_without_permission_on_object(obj, user):
    user_groups = user.groups.all()
    user_groups_with_permission = get_user_groups_with_permission_on_object(obj, user)

    return [g for g in user_groups if g not in user_groups_with_permission]

def has_permission(user, obj, permission):
    if obj.permission_type == "public":
        return True
    return user.has_perm(permission, obj)

def has_owner_permission(user, obj, permission):
    return user.has_perm(permission, obj)

def get_objects_for_user(user, perm, model, queryset=None):
    """
    Get Objects for a user according access type of object
    """
    model_name = model._meta.model_name
    if model_name not in ["profile", "dataset", "profilecategory"]:
        return model.objects.none()

    app_label = model._meta.app_label
    codename = get_perms_for_model(model).filter(
        codename__contains=perm
    ).first().codename

    if not codename:
        return model.objects.none()

    if not queryset:
        queryset = model.objects.all()
    queryset = queryset.exclude(**{"permission_type": "private"})
    queryset |= guardian_objects_for_user(
        user, f'{app_label}.{codename}', accept_global_perms=False
    )

    return queryset

