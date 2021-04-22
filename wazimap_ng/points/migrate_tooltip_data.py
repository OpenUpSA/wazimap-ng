

from wazimap_ng.points.models import ProfileCategory

def migrate_attributes():
    query = ProfileCategory.objects.all()

    for data in query:
        tooltip = data.visible_tooltip_attributes
        new_tooltip_data = []

        if isinstance(tooltip, dict):
            new_tooltip_data = tooltip.values()

        if new_tooltip_data:
            data.visible_tooltip_attributes = new_tooltip_data
            data.save()
