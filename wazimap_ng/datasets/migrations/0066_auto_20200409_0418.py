# Generated by Django 2.2.10 on 2020-04-09 04:18

import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import wazimap_ng.datasets.models.upload


def copy_data_to_new_field(apps, schema_editor):
    """
    copy data of Array field subindicator to json field subindicator
    """
    ProfileIndicator = apps.get_model('datasets', 'profileIndicator')

    for pi in ProfileIndicator.objects.all():
        if pi.subindicators:
            groups = pi.indicator.groups
            data = []
            if groups and len(groups) > 1:
                for idx, subindicator in enumerate(pi.subindicators):
                    subdata = {}
                    subindicators = subindicator.split("/")
                    for idx, val in enumerate(groups):
                        subdata[val] = subindicators[idx]
                    data.append(subdata)
            elif groups and len(groups) == 1:
                for idx, subindicator in enumerate(pi.subindicators):
                    data.append({groups[0] : subindicator})

            indicator_subindicators = pi.indicator.subindicators
            for idx, val in enumerate(data):
                for subindicator in indicator_subindicators:
                    if val.items() == subindicator["groups"].items():
                        data[idx] = {
                            "id": subindicator["id"],
                            "label": subindicator["label"],
                            "groups": val
                        }
            pi.subindicators_new = data
            pi.save()


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0065_auto_20200409_0526'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileindicator',
            name='subindicators_new',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list),
        ),
        migrations.RunPython(copy_data_to_new_field),
        migrations.RemoveField(
            model_name='profileindicator',
            name='subindicators',
        ),
        migrations.RenameField(
            model_name='profileindicator',
            old_name='subindicators_new',
            new_name='subindicators',
        ),
    ]