# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-18 18:23
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foro', '0003_auto_20160822_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forum',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from=b'title', unique=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from=b'title', unique=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from=b'title', unique=True),
        ),
    ]