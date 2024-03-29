# Generated by Django 2.2.13 on 2021-04-21 04:53

import django.contrib.postgres.fields.jsonb
from django.db import migrations

def save_profile_category(apps, schema_editor):
    ProfileCategory = apps.get_model('points', 'ProfileCategory')
    for pc in ProfileCategory.objects.all():
        tooltip = pc.visible_tooltip_attributes
        new_tooltip_data = []

        if isinstance(tooltip, dict):
            new_tooltip_data = list(tooltip.values())

        pc.visible_tooltip_attributes = new_tooltip_data
        pc.save()

class Migration(migrations.Migration):

    dependencies = [
        ('points', '0041_profilecategory_attributes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilecategory',
            name='visible_tooltip_attributes',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
        migrations.RunPython(save_profile_category, lambda apps, schema_editor: migrations.RunPython.noop),
    ]
