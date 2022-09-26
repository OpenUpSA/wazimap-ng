# Generated by Django 2.2.28 on 2022-09-16 07:20

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0049_auto_20220808_0720'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaltheme',
            name='color',
            field=colorfield.fields.ColorField(default='#000000', image_field=None, max_length=18, samples=[('#3a70ff', 'theme-1'), ('#993aff', 'theme-2'), ('#ad356d', 'theme-3'), ('#f04f4f', 'theme-4'), ('#ff3a8c', 'theme-5'), ('#ff893a', 'theme-6'), ('#e7bc20', 'theme-7'), ('#48c555', 'theme-8'), ('#2ccaad', 'theme-9'), ('#0a8286', 'theme-10')]),
        ),
        migrations.AddField(
            model_name='theme',
            name='color',
            field=colorfield.fields.ColorField(default='#000000', image_field=None, max_length=18, samples=[('#3a70ff', 'theme-1'), ('#993aff', 'theme-2'), ('#ad356d', 'theme-3'), ('#f04f4f', 'theme-4'), ('#ff3a8c', 'theme-5'), ('#ff893a', 'theme-6'), ('#e7bc20', 'theme-7'), ('#48c555', 'theme-8'), ('#2ccaad', 'theme-9'), ('#0a8286', 'theme-10')]),
        ),
    ]
