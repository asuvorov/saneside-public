# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-11 00:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('social_app', models.CharField(choices=[(b'--------', '--------'), (b'0', 'Facebook'), (b'1', 'Twitter'), (b'2', 'Linked In'), (b'4', 'Google +'), (b'8', 'Pinterest'), (b'16', 'Instagram'), (b'32', 'Tumblr')], default=b'--------', help_text='Social App', max_length=16, verbose_name='Social App')),
                ('url', models.URLField(blank=True, db_index=True, help_text='Social Link', null=True, verbose_name='url')),
                ('object_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('content_type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['created'],
                'verbose_name': 'social link',
                'verbose_name_plural': 'social links',
            },
        ),
    ]
