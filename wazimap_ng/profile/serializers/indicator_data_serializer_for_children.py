import logging
from collections.abc import Iterable
from itertools import groupby
from typing import Dict

from django.db.models import F

from wazimap_ng.datasets.models import Dataset, Group, IndicatorData
from wazimap_ng.profile.models import Profile
from wazimap_ng.utils import expand_nested_list, mergedict, qsdict

from .. import models

logger = logging.getLogger(__name__)


def get_profile_data(profile, geographies, version):
    return get_indicator_data(profile, profile.indicators.all(), geographies, version)


def get_indicator_data(profile, indicators, geographies, version):

    data = (IndicatorData.objects
            .filter(
                indicator__in=indicators,
                indicator__profileindicator__profile=profile,
                geography__in=geographies,
                indicator__dataset__version=version,
            )
            .values(
                jsdata=F("data"),
                profile_indicator_label=F("indicator__profileindicator__label"),
                subcategory=F("indicator__profileindicator__subcategory__name"),
                category=F("indicator__profileindicator__subcategory__category__name"),
                dataset=F("indicator__dataset"),
                geography_code=F("geography__code"),
            )
            .order_by("indicator__profileindicator__order")
            )
    return data


def IndicatorDataSerializerForChildren(profile, geography, version):
    children = geography.get_child_geographies(version)
    children_indicator_data = get_profile_data(profile, children, version)

    subcategories = (models.IndicatorSubcategory.objects.filter(category__profile=profile)
                     .order_by("category__order", "order")
                     .select_related("category")
                     )

    c = qsdict(subcategories,
               lambda x: x.category.name,
               lambda x: {"description": x.category.description}
               )

    s = qsdict(subcategories,
               lambda x: x.category.name,
               lambda x: "subcategories",
               "name",
               lambda x: {"description": x.description}
               )

    d5 = qsdict(children_indicator_data,
                "category",
                lambda x: "subcategories",
                "subcategory",
                lambda x: "indicators",
                "profile_indicator_label",
                lambda x: "data",
                "geography_code",
                "jsdata",
                )

    new_dict = {}
    mergedict(new_dict, c)
    mergedict(new_dict, s)
    mergedict(new_dict, d5)

    return new_dict
