# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models
import organizations.models
import django_extensions.db.fields
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(help_text='Team Name', max_length=200, verbose_name='Team', db_index=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'team',
                'verbose_name_plural': 'teams',
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('position', models.CharField(max_length=200, blank=True, help_text='Team Member Position', null=True, verbose_name='Position', db_index=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'team member',
                'verbose_name_plural': 'team members',
            },
        ),
        migrations.CreateModel(
            name='UserLogin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('ip', models.CharField(help_text='User IP Address', max_length=16, verbose_name='IP', db_index=True)),
                ('provider', models.CharField(default=b'Desktop', help_text='User Internet Provider', max_length=64, verbose_name='Provider')),
                ('country', django_extensions.db.fields.json.JSONField(null=True, blank=True)),
                ('city', django_extensions.db.fields.json.JSONField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'user login',
                'verbose_name_plural': 'user logins',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('avatar', models.ImageField(upload_to=b'images/accounts/avatars', blank=True)),
                ('nickname', models.CharField(max_length=32, blank=True, help_text='User Nickname', null=True, verbose_name='Nickname', db_index=True)),
                ('bio', models.TextField(help_text='USer Bio', null=True, verbose_name=b'Bio', blank=True)),
                ('gender', models.CharField(default=b'1', help_text='User Gender', max_length=2, verbose_name='Gender', choices=[(b'1', 'Male'), (b'0', 'Female')])),
                ('birth_day', models.DateField(help_text='User Birthday', null=True, verbose_name='Birthday', db_index=True, blank=True)),
                ('receive_newsletters', models.BooleanField(default=False, help_text='I would like to receive Email Updates', verbose_name='I would like to receive Email Updates')),
                ('privacy_mode', models.CharField(default=b'1', help_text='User Privacy Mode', max_length=2, verbose_name='Privacy Mode', choices=[(b'0', 'Paranoid'), (b'1', 'Normal')])),
                ('fb_profile', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ['user__first_name', 'user__last_name'],
                'verbose_name': 'user profile',
                'verbose_name_plural': 'user profiles',
            },
            bases=(core.models.ViewMixin, core.models.CommentMixin, core.models.RatingMixin, organizations.models.OrganizationStaffMixin, models.Model),
        ),
    ]
