# Generated by Django 2.2.10 on 2020-04-06 12:48

from django.db import migrations


def forwards(apps, schema_editor):
    """
    create initial data for Licence model
    """
    ProfileIndicator = apps.get_model('datasets', 'profileIndicator')
    ProfileKeyMetrics = apps.get_model('profile', 'ProfileKeyMetrics')

    for pi in ProfileIndicator.objects.filter(key_metric=True):
    	ProfileKeyMetrics.objects.create(
    		variable=pi.indicator,
    		subcategory=pi.subcategory,
                subindicator=0,
                denominator='absolute_value'
    	)


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0008_profilekeymetrics'),
    ]

    operations = [
    	migrations.RunPython(forwards, backwards)
    ]