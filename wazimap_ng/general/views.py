import logging

from django.views.decorators.http import condition
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, Http404

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

from django_q.tasks import result, fetch

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def consolidated_profile_helper(profile_id, geography_code, version_name):
    profile = get_object_or_404(profile_models.Profile, pk=profile_id)
    if version_name is None:
        version_name = profile.geography_hierarchy.default_version
    version = get_object_or_404(dataset_models.Version, name=version_name)
    geography = get_object_or_404(
        dataset_models.Geography,
        code=geography_code,
        geographyboundary__version=version
    )
    profile_js = profile_serializers.ExtendedProfileSerializer(profile, geography, version)
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
    })

@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def consolidated_profile(request, profile_id, geography_code):
    version = request.GET.get('version', None)
    js = consolidated_profile_helper(profile_id, geography_code, version)
    return Response(js)


@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def boundary_point_count(request, profile_id, geography_code):
    profile = get_object_or_404(profile_models.Profile, pk=profile_id)

    version_name = request.GET.get('version', None)
    if not version_name:
        version_name = profile.geography_hierarchy.default_version
    version = get_object_or_404(dataset_models.Version, name=version_name)

    geography = dataset_models.Geography.objects.get(code=geography_code, geographyboundary__version=version)
    return Response(point_views.boundary_point_count_helper(profile, geography, version))

@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def consolidated_versioned_data(request, profile_id, geography_code):
    profile = get_object_or_404(profile_models.Profile, pk=profile_id)
    codes = geography_code.split(":")
    geo_code, versions = codes[0], codes[1:]
    versions_list = profile.geography_hierarchy.configuration.get("versions", [])
    versions = list(set(versions_list).intersection(versions))
    version_objs = list(dataset_models.Version.objects.filter(name__in=versions))

    geography = dataset_models.Geography.objects.get(code=geo_code)

    if not version_objs or not geography:
        raise Http404
    js = profile_serializers.ExtendedProfileSerializer(profile, geography, version_objs)
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
def notifications_view(request):
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



@api_view(["GET"])
def task_status(request, task_id):
    """
    List the result for a task id
    We don't check if the task exist, since we can't get it from django until it's either errored or done
    """
    if request.method == "GET":
        response = dict(id=task_id, status="error")
        task = fetch(task_id)
        if not task:
            response.update({"status": "running"})
            return Response(response)
        if task.success:
            response.update({"status": "success"})
            return Response(response)
        return Response(response)
