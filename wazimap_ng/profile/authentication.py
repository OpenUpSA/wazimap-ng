import json
import logging

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.permissions import BasePermission

from .services import authentication
from .models import Profile

logger = logging.getLogger(__name__)


class ProfilePermissions(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        resolver = request.resolver_match
        if resolver is not None and "profile_id" in resolver.kwargs:
            profile = get_object_or_404(Profile, pk=resolver.kwargs["profile_id"])
            if authentication.requires_authentication(profile):
                logger.info(f"{profile} needs authentication")
                has_permission = authentication.has_permission(user, profile)
                logger.info(f"User: {user} has permission: {has_permission}")

                return has_permission
            else:
                logger.info(f"{profile} does not need authentication")
                return True

        logger.info(f"Could not determine profile request")
        return True
