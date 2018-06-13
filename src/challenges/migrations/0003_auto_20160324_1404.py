# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('challenges', '0002_auto_20160324_1404'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='organization',
            field=models.ForeignKey(blank=True, to='organizations.Organization', help_text='Challenge Organization', null=True, verbose_name='Organization'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated List of Tags.', verbose_name='Tags'),
        ),
    ]
