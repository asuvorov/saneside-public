# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-02 19:59
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20171023_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('avatar', models.ImageField(blank=True, upload_to=home.models.partner_directory_path)),
                ('name', models.CharField(blank=True, db_index=True, default=b'', help_text='Name', max_length=128, null=True, verbose_name='Name')),
                ('website', models.URLField(blank=True, db_index=True, help_text='Organization Website', null=True, verbose_name='Website')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'partner',
                'verbose_name_plural': 'partners',
            },
        ),
    ]
