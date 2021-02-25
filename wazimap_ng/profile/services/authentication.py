import logging

from django.contrib.auth.models import Group, User

logger = logging.getLogger(__name__)

def requires_authentication(profile):
    return profile.permission_type == "private"

def has_permission(user, profile):
    if user.is_superuser:
        logging.info("superuser has permission")
        return True

    if not requires_authentication(profile):
        logging.info("profile does not require authentication")
        return True

    if not user.is_authenticated:
        logging.info("user is rejected because they are not authenticaate")
        return False

    # TODO this is hacky for now
    # There should be a more explicit link between groups and profile
    if user.groups.filter(name__iexact=profile.name).count() > 0:
        logging.info("User has permission because of group membership")
        return True

    logging.info("Not other criteria matched - rejected login attempt")
    return False
