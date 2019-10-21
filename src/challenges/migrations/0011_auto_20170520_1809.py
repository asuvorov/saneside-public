# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-05-21 01:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0010_auto_20170403_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='challenge',
            field=models.ForeignKey(blank=True, help_text='Challenge', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='challenge_roles', to='challenges.Challenge', verbose_name='Challenge'),
        ),
    ]