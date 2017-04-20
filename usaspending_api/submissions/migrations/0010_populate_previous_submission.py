# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-01 18:30
from __future__ import unicode_literals

from django.db import migrations


def populate_previous_submission(apps, schema_editor):
    """
    For each submission, fill in the previous submission for the
    same fiscal year (if there is one)
    """
    submissions = apps.get_model("submissions", "SubmissionAttributes")

    # get QuerySet of submissions in ordered by cgac and descending order
    # by fiscal year and quarter
    # note: migration explicitly excludes non-broker submissions and
    # submissions that are not in quarterly format (since we have some
    # monthy test submissions loaded)
    subs = submissions.objects \
        .filter(broker_submission_id__isnull=False, quarter_format_flag=True) \
        .order_by('cgac_code', '-reporting_fiscal_year', '-reporting_fiscal_quarter')

    total_submissions = subs.count()

    # loop through to find linkages between submissions with the same CGAC
    # and fiscal year. not the nicest code, but should suffice for migration
    # purposes, since there aren't that many records in the submission table
    for i, s in enumerate(subs):
        if i < total_submissions - 1:
            if (s.cgac_code == subs[i + 1].cgac_code and
                    s.reporting_fiscal_year == subs[i + 1].reporting_fiscal_year):
                # the next record in the QuerySet has the same CGAC and FY,
                # so link it to the current submission
                s.previous_submission = subs[i + 1]
                s.save()


def clear_previous_submission(apps, schema_editor):
    """Set previous submission back to null."""
    subs = apps.get_model("submissions", "SubmissionAttributes")
    broker_subs = subs.objects.filter(
        broker_submission_id__isnull=False)

    for s in broker_subs:
        s.previous_submission = None
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0009_submissionattributes_previous_submission'),
    ]

    operations = [
        migrations.RunPython(populate_previous_submission, clear_previous_submission),
    ]
