from guardian.shortcuts import (
    get_group_perms, get_perms_for_model, get_groups_with_perms
)

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
