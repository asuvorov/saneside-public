# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-01 19:52
from __future__ import unicode_literals

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20170918_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phone',
            name='mobile_phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, help_text='Please, use the International Format, e.g. +1-202-555-0114.', max_length=128, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='phone',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, help_text='Please, use the International Format, e.g. +1-202-555-0114.', max_length=128, null=True, verbose_name='Phone Number'),
        ),
    ]
