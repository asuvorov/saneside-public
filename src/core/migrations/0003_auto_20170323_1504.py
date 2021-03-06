# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-23 22:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_sociallink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sociallink',
            name='content_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content_type_social_links', to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='sociallink',
            name='social_app',
            field=models.CharField(choices=[(b'--------', '--------'), (b'0', 'Facebook'), (b'1', 'Twitter'), (b'2', 'Linked In'), (b'4', 'Google +'), (b'8', 'Pinterest'), (b'16', 'Instagram'), (b'32', 'Tumblr'), (b'64', 'YouTube')], default=b'--------', help_text='Social App', max_length=16, verbose_name='Social App'),
        ),
    ]
