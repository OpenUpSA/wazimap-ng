# Generated by Django 2.2.10 on 2020-04-11 06:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0070_auto_20200411_0621'),
    ]

    operations = [
        migrations.RunSQL('alter sequence datasets_profilehighlight_id_seq rename to profile_profilehighlight_id_seq;'),
    ]
