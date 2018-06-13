# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('challenges', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='address',
            field=models.ForeignKey(blank=True, to='core.Address', help_text='Challenge Location', null=True, verbose_name='Address'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='author',
            field=models.ForeignKey(related_name='posted_challenges', verbose_name='Author', to=settings.AUTH_USER_MODEL, help_text='Challenge Author'),
        ),
    ]
