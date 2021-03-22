from typing import Dict, Union

from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpRequest, JsonResponse
from django.http.response import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect
)
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import condition
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..boundaries import views as boundaries_views
from ..cache import etag_profile_updated, last_modified_profile_updated
from ..datasets import models as dataset_models
from ..points import views as point_views
from ..profile import models as profile_models
from ..profile import serializers as profile_serializers


def consolidated_profile_helper(profile_id: int, geography_code: str) -> Dict:
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
def consolidated_profile(request: HttpRequest, profile_id: int, geography_code: str) -> Response:
    js = consolidated_profile_helper(profile_id, geography_code)
    return Response(js)


@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def consolidated_profile_test(request: HttpRequest, profile_id: int, geography_code: str) -> Response:
    js = consolidated_profile_helper(profile_id, geography_code)
    return Response("test2")


def logout_view(request: HttpRequest) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
    logout(request)
    return redirect("version")


def authenticate_admin(user: User) -> bool:
    return user.is_staff or user.is_superuser


@user_passes_test(authenticate_admin)
@never_cache
def notifications_view(request: HttpRequest) -> JsonResponse:
    messages = request.session.pop("notifications", [])
    task_list = request.session.get("task_list", [])

    if messages and task_list:
        for message in messages:
            if "task_id" in message:
                task_list.remove(message["task_id"])
        request.session["task_list"] = task_list
    return JsonResponse({
        "task_list": task_list,
        "notifications": messages,
    })
