# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-19 13:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0004_auto_20161027_1215'),
        ('accounts', '0007_auto_20161005_0933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionprocess',
            name='submission',
        ),
        migrations.AddField(
            model_name='submissionattributes',
            name='broker_submission_id',
            field=models.IntegerField(default=0, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submissionattributes',
            name='usaspending_update',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='SubmissionProcess',
        ),
    ]
