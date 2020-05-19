from django.contrib.auth import get_permission_codename

from guardian.shortcuts import get_objects_for_user as guardian_objects_for_user
from .custom_permissions import queryset_filters, fk_queryset_filter, custom_permissions


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

    model_name, app_label = get_model_info(obj._meta.model)
    method_name = f"user_has_perm_for_{app_label}_{model_name}"

    if is_method(custom_permissions, method_name):
        return getattr(custom_permissions, method_name)(user, obj, permission)

    permission = permission_name(obj._meta, permission)

    if hasattr(obj._meta.model, "permission_type"):
        return user.has_perm(permission, obj)
    return user.has_perm(permission)

def get_objects_for_user(user, perm, model, queryset=None):
    """
    Get Objects for a user according access type of object
    """
    queryset = queryset or model.objects.all()

    if (user.is_superuser):
        return queryset

    if not hasattr(model, 'permission_type'):
        return model.objects.none()

    model_name, app_label = get_model_info(model)
    codename = get_permission_codename(perm, model._meta)

    if not codename:
        return model.objects.none()

    if not queryset:
        queryset = model.objects.all()

    queryset = queryset.exclude(**{"permission_type": "private"})
    queryset |= guardian_objects_for_user(
        user, f'{app_label}.{codename}', accept_global_perms=False
    )

    return queryset

def get_custom_queryset(user, model, queryset=None):
    """
    Get custom queryset for admin get_queryset
    """
    model_name, app_label = get_model_info(model)
    codename = get_permission_codename("view", model._meta)
    method_name = f"get_filters_for_{model_name}"
    qs_filters = {}

    if not codename:
        return model.objects.none()

    if not queryset:
        queryset = model.objects.all()

    if hasattr(model, 'permission_type'):
        queryset = queryset.exclude(**{"permission_type": "private"})
        queryset |= guardian_objects_for_user(
            user, f'{app_label}.{codename}', accept_global_perms=False
        )

    if is_method(queryset_filters, method_name):
        qs_filters = getattr(queryset_filters, method_name)(user)
        queryset = queryset.filter(**qs_filters)

    return queryset


def get_custom_fk_queryset(user, model):
    """
    Get custom queryset for fk of admin model
    """
    model_name, app_label = get_model_info(model)
    queryset = get_custom_queryset(user, model)
    method_name = f"get_filters_for_{model_name}"
    qs_filters = {}

    if is_method(fk_queryset_filter, method_name):
        qs_filters = getattr(fk_queryset_filter, method_name)(user)
        queryset = queryset.filter(**qs_filters)
    return queryset
