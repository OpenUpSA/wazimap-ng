# Generated by Django 2.2.10 on 2020-03-29 05:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boundaries', '0023_geographyboundary_geom_cache'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='geographyboundary',
            name='boundaries__code_8ea6f4_idx',
        ),
        migrations.RemoveField(
            model_name='geographyboundary',
            name='code',
        ),
        migrations.RemoveField(
            model_name='geographyboundary',
            name='name',
        ),
    ]
