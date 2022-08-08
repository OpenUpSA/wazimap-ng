from django import template
from django.urls import reverse
from wazimap_ng.datasets.models import Group

register = template.Library()

@register.filter
def get_subindicator_link(pi_obj):
    url = None
    if pi_obj:
        indicator = pi_obj.indicator
        group = Group.objects.filter(
            dataset=indicator.dataset, name=indicator.groups[0]
        ).first()
        if group:
            url = reverse("admin:datasets_group_change", args=(group.id,))
    return url
