from django.db import migrations
from wazimap_ng.datasets.tasks import indicator_data_extraction
from wazimap_ng.datasets.models import Indicator

def save_indicators(apps, schema_editor):
    for indicator in Indicator.objects.all():
        indicator_data_extraction(indicator)


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0111_auto_20210322_0740'),
    ]

    operations = [
        migrations.RunPython(save_indicators),
    ]

