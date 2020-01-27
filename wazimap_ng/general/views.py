from rest_framework.response import Response
from rest_framework.decorators import api_view

from ..datasets import models as dataset_models
from ..datasets import views as dataset_views
from ..boundaries import models as boundaries_models
from ..boundaries import views as boundaries_views

@api_view()
def consolidated_profile(request, profile_id, code):
    profile_js = dataset_views.profile_geography_data_helper(profile_id, code)
    boundary_js = boundaries_views.geography_item_helper(code)
    children_boundary_js = boundaries_views.geography_children_helper(code)

    parent_layers = []
    parents = profile_js["geography"]["parents"]
    for parent in parents:
        layer = boundaries_views.geography_children_helper(parent["code"])
        parent_layers.append(layer)

    return Response({
        "profile": profile_js,
        "boundary": boundary_js,
        "children": children_boundary_js,
        "parent_layers": parent_layers,
    })

@api_view()
def consolidated_profile_test(request, profile_id, code):
    profile_js = dataset_views.profile_geography_data_helper(profile_id, code)
    boundary_js = boundaries_views.geography_item_helper(code)
    children_boundary_js = boundaries_views.geography_children_helper(code)

    parent_layers = []
    parents = profile_js["geography"]["parents"]
    for parent in parents:
        layer = boundaries_views.geography_children_helper(parent["code"])
        parent_layers.append(layer)

    js = {
        "profile": profile_js,
        "boundary": boundary_js,
        "children": children_boundary_js,
        "parent_layers": parent_layers,
    }

    return Response("hello")
