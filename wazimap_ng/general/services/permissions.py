from typing import Tuple, Type, Union

from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Group, User
from django.db.models.base import Model
from django.db.models.query import QuerySet
from guardian.shortcuts import assign_perm, get_groups_with_perms
from guardian.shortcuts import get_objects_for_user as guardian_objects_for_user
from guardian.shortcuts import get_perms_for_model, remove_perm

from wazimap_ng.config.common import STAFF_GROUPS

from .custom_permissions import custom_permissions
from .custom_permissions.fk_queryset_filter import CustomFKQuerySet
from .custom_permissions.queryset_filters import CustomQuerySet


def get_user_group(user: User) -> QuerySet:
    return user.groups.all().exclude(
        name__in=STAFF_GROUPS
    ).first()


def assign_perms_to_group(profile_name: str, obj: Model, remove_previous_perms: bool = False) -> None:
    group, created = Group.objects.get_or_create(
        name=profile_name
    )
    old_groups = get_groups_with_perms(obj)

    for perm in get_perms_for_model(obj._meta.model):
        if remove_previous_perms:
            for old_group in old_groups:
                remove_perm(perm, old_group, obj)
        assign_perm(perm, group, obj)


def permission_name(opts, name: str) -> str:
    codename = get_permission_codename(name, opts)
    permission = f"{opts.app_label}.{codename}"
    return permission


def is_method(mod, name):
    return hasattr(mod, name) and callable(getattr(mod, name))


def get_model_info(model: Type[Model]) -> Tuple[Union[str, None], str]:
    meta_details = model._meta
    return meta_details.model_name, meta_details.app_label


def has_permission(user: User, obj: Model, permission: str) -> bool:
    if user.is_superuser or not obj:
        return True

    model = obj._meta.model
    model_name, app_label = get_model_info(obj._meta.model)
    method_name = f"user_has_perm_for_{app_label}_{model_name}"

    if is_method(custom_permissions, method_name):
        return getattr(custom_permissions, method_name)(user, obj, permission)

    permission = permission_name(obj._meta, permission)

    if hasattr(obj._meta.model, "permission_type"):
        return user.has_perm(permission, obj)
    return user.has_perm(permission)


def get_objects_for_user(
        user: User, model: Model, perm: str = "view", queryset: QuerySet = None, include_public: bool = True) -> QuerySet:
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


def get_custom_queryset(model: Type[Model], user: User) -> QuerySet:
    """
    Get custom queryset for admin get_queryset
    """
    model_name, app_label = get_model_info(model)
    method_name = f"get_{app_label}_{model_name}_queryset"

    queryset = CustomQuerySet(model)
    if is_method(CustomQuerySet, method_name):
        return getattr(queryset, method_name)(user)

    return queryset


def get_custom_fk_queryset(user: User, model: Type[Model]) -> QuerySet:
    """
    Get custom queryset for fk of admin model
    """
    model_name, app_label = get_model_info(model)
    method_name = f"get_{model_name}_queryset"

    queryset = CustomFKQuerySet(model)
    if is_method(CustomFKQuerySet, method_name):
        return getattr(queryset, method_name)(user)
    return queryset
