from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Group

from guardian.shortcuts import (
    get_perms_for_model, assign_perm,
    get_objects_for_user as guardian_objects_for_user
)

from .custom_permissions import fk_queryset_filter, custom_permissions

from .custom_permissions.queryset_filters import CustomQuerySet
from .custom_permissions.fk_queryset_filter import CustomFKQuerySet


def assign_perms_to_group(profile_name, obj):
    group, created = Group.objects.get_or_create(
        name=profile_name.lower()
    )
    for perm in get_perms_for_model(obj._meta.model):
        assign_perm(perm, group, obj)

def permission_name(opts, name):
    codename = get_permission_codename(name, opts)
    permission = f"{opts.app_label}.{codename}"
    return permission

def is_method(mod, name):
    return hasattr(mod, name) and callable(getattr(mod, name))

def get_model_info(model):
    meta_details = model._meta
    return meta_details.model_name, meta_details.app_label

def has_permission(user, obj, permission):
    if user.is_superuser or not obj:
        return True

    model = obj._meta.model
    model_name, app_label = get_model_info(obj._meta.model)
    method_name = f"user_has_perm_for_{app_label}_{model_name}"

    if is_method(custom_permissions, method_name):
        print("IN HERE __>>>")
        return getattr(custom_permissions, method_name)(user, obj, permission)

    permission = permission_name(obj._meta, permission)

    if hasattr(obj._meta.model, "permission_type"):
        return user.has_perm(permission, obj)
    return user.has_perm(permission)

def get_objects_for_user(
        user, model, perm="view", queryset=None, include_public=True
    ):
    """
    Get Objects for a user according access type of object
    """
    if queryset == None:
        queryset = model.objects.all()

    if not hasattr(model, 'permission_type'):
        return model.objects.none()

    model_name, app_label = get_model_info(model)
    codename = get_permission_codename(perm, model._meta)

    if not codename:
        return model.objects.none()

    if include_public:
        queryset = queryset.exclude(**{"permission_type": "private"})
        queryset |= guardian_objects_for_user(
            user, f'{app_label}.{codename}', accept_global_perms=False
        )
    else:
        queryset = guardian_objects_for_user(
            user, f'{app_label}.{codename}', accept_global_perms=False
        )

    return queryset

def get_custom_queryset(model, user):
    """
    Get custom queryset for admin get_queryset
    """
    model_name, app_label = get_model_info(model)
    method_name = f"get_{app_label}_{model_name}_queryset"

    queryset = CustomQuerySet(model)
    if is_method(CustomQuerySet, method_name):
        return getattr(queryset, method_name)(user)

    return queryset


def get_custom_fk_queryset(user, model):
    """
    Get custom queryset for fk of admin model
    """
    model_name, app_label = get_model_info(model)
    method_name = f"get_{model_name}_queryset"

    queryset = CustomFKQuerySet(model)
    if is_method(CustomFKQuerySet, method_name):
        return getattr(queryset, method_name)(user)
    return queryset
