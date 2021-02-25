from .. import permissions


def user_has_perm_for_datasets_indicator(user, obj, perm):
	permission = permissions.permission_name(obj.dataset._meta, perm)
	return user.has_perm(permission, obj.dataset)
