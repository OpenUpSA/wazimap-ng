from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r

profiles_list = [
    {
        "id": 1, "name": "Youth Explorer",
    },
    {
        "id": 2, "name": "Wazimap"
    },
]

profile_indicator_ids = {
    1: [1, 3],
    2: [1, 2, 4]
}

datasets_list = [
    {
        "id": 1, "name": "Census 2011",
    },
    {
        "id": 2, "name": "2016 Community Survey"
    },
]

indicators_list = {
    1: [
        {"id": 1, "name": "Population"},
        {"id": 2, "name": "Gender"},
        {"id": 3, "name": "Race"},
    ],
    2: [
        {"id": 4, "name": "Income"},
        {"id": 5, "name": "Crime"},
    ]
}

indicator_data = {
    1: [
        {"geography_id": 1, "geography": "Cape Town", "value": 100},
        {"geography_id": 2, "geography": "Johannesburg", "value": 200},
        {"geography_id": 3, "geography": "eThewini", "value": 300},
        {"geography_id": 3, "geography": "eThewini", "value": 300},
        {"geography_id": 4, "geography": "eThewini", "value": 300},
        {"geography_id": 5, "geography": "eThewini", "value": 300},
        {"geography_id": 6, "geography": "eThewini", "value": 300},
        {"geography_id": 7, "geography": "eThewini", "value": 300},
        {"geography_id": 8, "geography": "eThewini", "value": 300},
        {"geography_id": 9, "geography": "eThewini", "value": 300},
        {"geography_id": 10, "geography": "eThewini", "value": 300},
        {"geography_id": 11, "geography": "eThewini", "value": 300},
        {"geography_id": 12, "geography": "eThewini", "value": 300},
    ],
    2: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    3: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    4: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    5: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
}

@api_view()
def datasets(request):
    return Response(datasets_list)

@api_view()
def dataset_meta(request, dataset_id):
    for d in datasets_list:
        if d["id"] == dataset_id:
            return Response(d)

    raise Http404("Dataset does not exist")

@api_view()
def dataset_indicators(request, dataset_id):
    if dataset_id in indicators_list:
        return Response(indicators_list[dataset_id])

    raise Http404("Dataset does not exist")

@api_view()
def indicators(request):
    return Response(indicators_list)

@api_view()
def indicator_raw_data(request, indicator_id):
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(indicator_data[indicator_id], request)
    if page is not None:
        return paginator.get_paginated_response(page)

    return None

@api_view()
def indicator_geography(request, indicator_id, geography_id):
    data = indicator_data[indicator_id]
    datum = [
        d for d in data if d["geography_id"] == geography_id
    ]
    return Response(datum[0])

@api_view()
def profiles(request):
    return Response(profiles_list)

@api_view()
def profile_indicators(request, profile_id):
    indicator_ids = profile_indicator_ids[profile_id]
    indicators = []
    for dataset in indicators_list.values():
        for ind in dataset:
            if ind["id"] in indicator_ids:
                indicators.append(ind)

    return Response(indicators)

@api_view()
def profile_geography_data(request, profile_id, geography_id):
    all_data = {}
    indicator_ids = profile_indicator_ids[profile_id]
    for indicator_id in indicator_ids:
        data = indicator_data[indicator_id]
        for geo in data:
            if geo["geography_id"] == geography_id:
                all_data[indicator_id] = geo

    return Response(all_data)
