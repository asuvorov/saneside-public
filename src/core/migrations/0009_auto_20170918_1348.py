# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-18 20:48
from __future__ import unicode_literals

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20170714_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsletter',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, help_text='Newsletter Content', null=True, verbose_name='Content'),
        ),
    ]
