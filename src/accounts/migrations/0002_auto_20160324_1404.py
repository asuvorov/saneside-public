# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.ForeignKey(blank=True, to='core.Address', help_text='User Address', null=True, verbose_name='Address'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.ForeignKey(blank=True, to='core.Phone', help_text='User Phone Numbers', null=True, verbose_name='Phone Numbers'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(related_name='profile', verbose_name='User', to=settings.AUTH_USER_MODEL, help_text='User'),
        ),
        migrations.AddField(
            model_name='userlogin',
            name='user',
            field=models.ForeignKey(related_name='user_login', verbose_name='User', to=settings.AUTH_USER_MODEL, help_text='User'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(related_name='members', blank=True, to='accounts.Team', help_text='Team', null=True, verbose_name='Team'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='user',
            field=models.OneToOneField(related_name='team_member', verbose_name='Team Member', to=settings.AUTH_USER_MODEL, help_text='Team Member'),
        ),
    ]
