# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-09 17:25
from __future__ import unicode_literals

from django.db import migrations
from usaspending_api.etl.helpers import update_model_description_fields


def fix_default_fields(apps, schema_editor):
    award = apps.get_model("awards", "Award")
    transaction = apps.get_model("awards", "Transaction")
    legal_entity = apps.get_model("references", "LegalEntity")

    # We now handle default cases for descriptions better, and 'U' is a perfectly
    # valid award type now that we have updated DAIMS definitions. Therefore, any
    # prior assignment of a 'U' or 'UN' should be reversed to a null

    # If possible, it's a good idea to re-load any submission that might have used
    # a valid 'U' award type, but that we instead interpreted as "unknown"

    award.objects.filter(type='U').update(type=None)
    transaction.objects.filter(type='U').update(type=None)
    legal_entity.objects.filter(business_types='UN').update(business_types=None)


def update_descriptions(apps, schema_editor):
    update_model_description_fields()


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0079_auto_20170409_1723'),
        ('references', '0064_auto_20170409_1724')
    ]

    operations = [
        migrations.RunPython(fix_default_fields),
        migrations.RunPython(update_descriptions)
    ]
