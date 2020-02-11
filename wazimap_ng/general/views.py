from rest_framework.response import Response
from rest_framework.decorators import api_view

from ..datasets import models as dataset_models
from ..datasets import views as dataset_views
from ..boundaries import models as boundaries_models
from ..boundaries import views as boundaries_views

def consolidated_profile_helper(profile_id, code):
    profile_js = dataset_views.profile_geography_data_helper(profile_id, code)
    boundary_js = boundaries_views.geography_item_helper(code)
    children_boundary_js = boundaries_views.geography_children_helper(code)

    parent_layers = []
    parents = profile_js["geography"]["parents"]
    children_levels = [p["level"] for p in parents[1:]] + [profile_js["geography"]["level"]]
    pairs = zip(parents, children_levels)
    for parent, children_level in pairs:
        layer = boundaries_views.geography_children_helper(parent["code"])
        parent_layers.append(layer[children_level])

    return ({
        "profile": profile_js,
        "boundary": boundary_js,
        "children": children_boundary_js,
        "parent_layers": parent_layers,
    })

@api_view()
def consolidated_profile(request, profile_id, code):
    js = consolidated_profile_helper(profile_id, code)
    return Response(js)

@api_view()
def consolidated_profile_test(request, profile_id, code):
    js = consolidated_profile_helper(profile_id, code)
    return Response("test")
