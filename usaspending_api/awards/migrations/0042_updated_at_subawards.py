# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-09-04 20:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0041_subaward_sans_le'),
    ]

    operations = [
        migrations.AddField(
            model_name='subaward',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]