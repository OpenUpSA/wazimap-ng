from django.views.decorators.http import condition
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.template.loader import render_to_string

from rest_framework.response import Response
from rest_framework.decorators import api_view

from ..profile import models as profile_models
from ..profile import serializers as profile_serializers
from ..datasets import models as dataset_models
from ..datasets import views as dataset_views
from ..boundaries import models as boundaries_models
from ..boundaries import views as boundaries_views
from ..cache import etag_profile_updated, last_modified_profile_updated
from ..points import views as point_views
from ..points import models as point_models

from .models import Notification


def consolidated_profile_helper(profile_id, geography_code):
    profile = get_object_or_404(profile_models.Profile, pk=profile_id)
    version = profile.geography_hierarchy.root_geography.version
    geography = dataset_models.Geography.objects.get(code=geography_code, version=version)

    profile_js = profile_serializers.ExtendedProfileSerializer(profile, geography)
    boundary_js = boundaries_views.geography_item_helper(geography_code, version)
    children_boundary_js = boundaries_views.geography_children_helper(geography_code, version)

    parent_layers = []
    parents = profile_js["geography"]["parents"]
    children_levels = [p["level"] for p in parents[1:]] + [profile_js["geography"]["level"]]
    pairs = zip(parents, children_levels)
    for parent, children_level in pairs:
        layer = boundaries_views.geography_children_helper(parent["code"], version)
        if children_level in layer:
            parent_layers.append(layer[children_level])

    return ({
        "profile": profile_js,
        "boundary": boundary_js,
        "children": children_boundary_js,
        "parent_layers": parent_layers,
        "themes": point_views.boundary_point_count_helper(profile, geography)
    })

@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def consolidated_profile(request, profile_id, geography_code):
    js = consolidated_profile_helper(profile_id, geography_code)
    return Response(js)

@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def consolidated_profile_test(request, profile_id, geography_code):
    js = consolidated_profile_helper(profile_id, geography_code)
    return Response("test2")

from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect("version")


def authenticate_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(authenticate_admin)
@never_cache
def notifications_delete(request, pk):
    notification = Notification.objects.filter(id=pk).first()

    notification.deleted = True
    notification.unread = False
    notification.save()
    return JsonResponse({ "deleted": True })

@user_passes_test(authenticate_admin)
@never_cache
def notifications_delete_all(request):
    request.user.notifications.filtered_qs().update(
        deleted = True, unread=False
    )
    return JsonResponse({ "deleted": True })

@user_passes_test(authenticate_admin)
@never_cache
def unread_notifications(request):
    data = []
    unread_notifications = request.user.notifications.unread()

    for notification in request.user.notifications.unread():
        html = render_to_string(
            'admin/subtemplate/notification_msg.html',
            {"notification": notification}
        )
        data.append({
            "id": notification.id,
            "html": html,
            "level": notification.level,
        })
    return JsonResponse({ "results": data })
