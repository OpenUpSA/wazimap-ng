from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r
import copy
from .models import Profile

profiles_list = [
    {
        "id": 1, "name": "Youth Explorer",
    },
    {
        "id": 2, "name": "Wazimap"
    },
]

datasets_list = [
    {
        "id": 1, "name": "2016 Community Survey",
    },
    {
        "id": 2, "name": "2016 Community Survey"
    },
]

indicators_list = {
    1: [
        {"id": 1, "name": "People"},
        {"id": 2, "name": "Youth aged 15-24"},
        {"id": 3, "name": "Total population by age group", "classes": [
            "0-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65+"
        ]},
        {"id": 4, "name": "Youth population by race"},
        {"id": 5, "name": "Youth population by gender"},
        {"id": 6, "name": "Language most spoken at home"},
        {"id": 7, "name": "Born in South Africa"},
        {"id": 8, "name": "Youth by region of birth"},
        {"id": 9, "name": "Youth by province of birth"},
        {"id": 10, "name": "Youth citizens"},
        {"id": 11, "name": "Progress through school"},
        {"id": 12, "name": "Youth aged 16-17 by grade 9 completion"},
        {"id": 13, "name": "Youth aged 16-17 who completed grade 9 by gender"},

    ],
    2: [
        {"id": 14, "name": "Income"},
        {"id": 15, "name": "Crime"},
    ]
}

profile_indicator_ids = {
    1: [
            {
                "category": "Youth Demographics", "sub-categories": [
                    {"name": "Population", "indicators": [indicators_list[1][i] for i in range(0, 5)]},
                    {"name": "Language", "indicators": [indicators_list[1][i] for i in [5]]},
                    {"name": "Migration", "indicators": [indicators_list[1][i] for i in [6, 7, 8]]},
                    {"name": "Citizenship", "indicators": [indicators_list[1][i] for i in [9]]},
                ]
            },
            {
                "category": "Youth Education", "sub-categories": [
                    {"name": "Progress through school", "indicators": [indicators_list[1][i] for i in [10, 11, 12]]},
                ]
            },
    ],
    2: [
            {
                "category": "Demographics", "sub-categories": [
                    {"name": "Age", "indicators": [1]},
                    {"name": "Population", "indicators": [2]},
                ]
            },
            {
                "category": "Income", "sub-categories": [
                    {"name": "Household", "indicators": [4]},
                ]
            },
    ],
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
    6: [
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
    7: [
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
    8: [
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
    9: [
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
    10: [
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
    11: [
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
    12: [
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
    13: [
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
    return Response(profile_indicator_ids[profile_id])
        
    indicator_ids = profile_indicator_ids[profile_id]
    indicators = []
    for dataset in indicators_list.values():
        for ind in dataset:
            if ind["id"] in indicator_ids:
                indicators.append(ind)

    return Response(indicators)


def extract_indicators(profile):
    all_indicators = []
    for category in profile:
        for subcategory in category["sub-categories"]:
            for indicator in subcategory["indicators"]:
                all_indicators.append(indicator["id"])

    return all_indicators

def get_indicator(indicator_id):
    for dataset_id, indicators in indicators_list.items():
        for indicator in indicators:
            if indicator["id"] == indicator_id:
                return indicator

@api_view()
def profile_geography_data(request, profile_id, geography_id):
    profile = Profile.objects.get(id=geography_id)
    return Response(profile.data)
