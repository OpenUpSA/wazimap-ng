# Generated by Django 2.2.10 on 2020-04-10 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0068_auto_20200410_1712'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilehighlight',
            name='as_percentage',
        ),
        migrations.RemoveField(
            model_name='profilehighlight',
            name='denominator',
        ),
    ]