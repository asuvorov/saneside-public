# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-23 00:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foro', '0002_auto_20160423_1345'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created'], 'verbose_name': 'forum topic post', 'verbose_name_plural': 'forum topic posts'},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ['-created'], 'verbose_name': 'forum topic', 'verbose_name_plural': 'forum topics'},
        ),
    ]