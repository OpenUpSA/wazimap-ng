from rest_framework.permissions import BasePermission
from .services import authentication
from .models import Profile

class ProfileAuthentication(BasePermission):
    def has_permission(self, request, view):
        resolver = request.resolver_match
        if resolver is not None and "profile_id" in resolver.kwargs:
            profile = Profile.objects.get(pk=resolver.kwargs["profile_id"])
            return not authentication.requires_authentication(profile)
        return False
