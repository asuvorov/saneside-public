# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-18 20:39
from __future__ import unicode_literals

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='answer',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, help_text='Answer', null=True, verbose_name='Answer'),
        ),
    ]
