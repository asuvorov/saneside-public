# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2016-12-27 23:22
from __future__ import unicode_literals

from django.db import migrations, models
import select_multiple_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0008_challenge_addressless'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='addressless',
            field=models.BooleanField(default=False, help_text='I will provide the Location later, if any.', verbose_name='I will provide the Location later, if any.'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='day_of_month',
            field=select_multiple_field.models.SelectMultipleField(choices=[(b'0', b'0'), (b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'10'), (b'11', b'11'), (b'12', b'12'), (b'13', b'13'), (b'14', b'14'), (b'15', b'15'), (b'16', b'16'), (b'17', b'17'), (b'18', b'18'), (b'19', b'19'), (b'20', b'20'), (b'21', b'21'), (b'22', b'22'), (b'23', b'23'), (b'24', b'24'), (b'25', b'25'), (b'26', b'26'), (b'27', b'27'), (b'28', b'28'), (b'29', b'29'), (b'30', b'30'), (b'31', b'31')], default=b'0', help_text='Day of Month', max_length=64, verbose_name='Day of Month'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='day_of_week',
            field=select_multiple_field.models.SelectMultipleField(choices=[(b'-1', '----------'), (b'0', 'Sunday'), (b'1', 'Monday'), (b'2', 'Tuesday'), (b'3', 'Wednesday'), (b'4', 'Thursday'), (b'5', 'Friday'), (b'6', 'Saturday')], default=b'-1', help_text='Day of Week', max_length=64, verbose_name='Day of Week'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='month',
            field=select_multiple_field.models.SelectMultipleField(choices=[(b'-1', '----------'), (b'1', 'January'), (b'2', 'February'), (b'3', 'March'), (b'4', 'April'), (b'5', 'May'), (b'6', 'June'), (b'7', 'July'), (b'8', 'August'), (b'9', 'September'), (b'10', 'October'), (b'11', 'November'), (b'12', 'December')], default=b'-1', help_text='Month', max_length=64, verbose_name='Month'),
        ),
    ]