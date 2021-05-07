# Generated by Django 2.2.13 on 2021-05-07 11:17

from django.db import migrations, models

def reorder_themes(apps, schema_editor):
    Theme = apps.get_model("points", "Theme")
    order = 0
    for item in Theme.objects.all():
        order += 1
        item.order = order
        item.save()

def reorder_cateogories(apps, schema_editor):
    Category = apps.get_model("points", "ProfileCategory")
    order = 0
    for item in Category.objects.all():
        order += 1
        item.order = order
        item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('points', '0041_profilecategory_attributes'),
    ]

    operations = [
        migrations.RunPython(reorder_themes),
        migrations.RunPython(reorder_cateogories),
    ]
