# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-23 22:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_partner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='website',
            field=models.URLField(blank=True, db_index=True, help_text='Website', null=True, verbose_name='Website'),
        ),
    ]
