# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0003_auto_20160324_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='duration',
            field=models.PositiveIntegerField(default=1, help_text='Challenge Duration', verbose_name='Duration (hours)'),
        ),
    ]
