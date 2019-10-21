# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 01:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0004_auto_20160324_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='start_date_time_tz',
            field=models.DateTimeField(blank=True, db_index=True, help_text='Challenge Start Date/Time with TZ', null=True, verbose_name='Start Date/Time with TZ'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='start_tz',
            field=models.CharField(blank=True, db_index=True, help_text='Challenge Timezone', max_length=255, null=True, verbose_name='Timezone'),
        ),
    ]