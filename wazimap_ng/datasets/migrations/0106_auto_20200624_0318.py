# Generated by Django 2.2.10 on 2020-06-24 03:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0105_auto_20200624_0311'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dataset',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
