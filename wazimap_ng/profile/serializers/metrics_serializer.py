from typing import Callable, Dict, List, Union

from django.db.models.query import QuerySet

from wazimap_ng.datasets.models import IndicatorData
from wazimap_ng.datasets.models.geography import Geography
from wazimap_ng.profile.models import Profile, ProfileKeyMetrics
from wazimap_ng.utils import mergedict

from .helpers import MetricCalculator


def get_indicator_data(profile_key_metric: ProfileKeyMetrics, geographies: List[Geography]) -> QuerySet:
    indicator_data = IndicatorData.objects.filter(
        indicator__profilekeymetrics=profile_key_metric, geography__in=geographies)
    return indicator_data


def absolute_value(profile_key_metric: ProfileKeyMetrics, geography: Geography) -> float:
    data = get_indicator_data(profile_key_metric, [geography]).first().data
    return MetricCalculator.absolute_value(data, profile_key_metric, geography)


def subindicator(profile_key_metric: ProfileKeyMetrics, geography: Geography) -> Union[float, None]:
    data = get_indicator_data(profile_key_metric, [geography]).first().data
    return MetricCalculator.subindicator(data, profile_key_metric, geography)


def sibling(profile_key_metric: ProfileKeyMetrics, geography: Geography) -> Union[float, None]:
    siblings = geography.get_siblings()
    data = get_indicator_data(profile_key_metric, [geography] + siblings)
    return MetricCalculator.sibling(data, profile_key_metric, geography)


algorithms: Dict[str, Callable] = {
    "absolute_value": absolute_value,
    "sibling": sibling,
    "subindicators": subindicator
}


def MetricsSerializer(profile: Profile, geography: Geography) -> Dict:
    out_js: Dict = {}
    profile_key_metrics = (ProfileKeyMetrics.objects
                           .filter(profile=profile)
                           .order_by("order")
                           .select_related("subcategory", "subcategory__category")
                           )
    for profile_key_metric in profile_key_metrics:
        denominator: str = profile_key_metric.denominator
        method: Callable = algorithms.get(denominator, absolute_value)
        val: float = method(profile_key_metric, geography)
        if val is not None:
            js = {
                profile_key_metric.subcategory.category.name: {
                    "subcategories": {
                        profile_key_metric.subcategory.name: {
                            "key_metrics": [{
                                "label": profile_key_metric.label,
                                "value": val,
                                "method": denominator
                            }]
                        }
                    }
                }

            }

            mergedict(out_js, js)

    return out_js
