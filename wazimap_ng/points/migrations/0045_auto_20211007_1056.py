# Generated by Django 2.2.24 on 2021-10-07 10:56

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0044_auto_20210909_0748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilecategory',
            name='description',
            field=tinymce.models.HTMLField(blank=True),
        ),
    ]
