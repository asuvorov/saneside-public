# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-23 22:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20171023_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='question',
            field=models.TextField(help_text='Question', max_length=1024, verbose_name='Question'),
        ),
    ]
