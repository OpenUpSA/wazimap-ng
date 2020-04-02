from django.views.decorators.http import condition
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.decorators import api_view

from ..datasets import models as dataset_models
from ..datasets import views as dataset_views
from ..boundaries import models as boundaries_models
from ..boundaries import views as boundaries_views
from ..cache import etag_profile_updated, last_modified_profile_updated
from ..points import views as point_views
from ..points import models as point_models

def consolidated_profile_helper(profile_id, geography_code):
    profile = get_object_or_404(dataset_models.Profile, pk=profile_id)
    version = profile.geography_hierarchy.root_geography.version

    profile_js = dataset_views.profile_geography_data_helper(profile_id, geography_code)
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
        "themes": point_views.boundary_point_count_helper(profile_id, geography_code)
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
