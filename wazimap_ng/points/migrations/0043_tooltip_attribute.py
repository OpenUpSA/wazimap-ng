from django.db import migrations
from wazimap_ng.points.models import ProfileCategory

def save_profile_category(apps, schema_editor):
    query = ProfileCategory.objects.all()

    for data in query:
        tooltip = data.visible_tooltip_attributes
        new_tooltip_data = []

        if isinstance(tooltip, dict):
            new_tooltip_data = list(tooltip.values())

        data.visible_tooltip_attributes = new_tooltip_data
        data.save()


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0042_auto_20210421_0453'),
    ]

    operations = [
        migrations.RunPython(save_profile_category),
    ]
