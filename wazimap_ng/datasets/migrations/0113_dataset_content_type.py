# Generated by Django 2.2.21 on 2021-07-02 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0112_auto_20210527_0541'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='content_type',
            field=models.CharField(choices=[('quantitative', 'quantitative'), ('qualitative', 'qualitative')], default='quantitative', max_length=32),
        ),
    ]
