# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models
import taggit.managers
import django_extensions.db.fields
import autoslug.fields
from django.conf import settings
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('avatar', models.ImageField(upload_to=b'images/organizations/avatars')),
                ('name', models.CharField(help_text='Organization Name', max_length=80, verbose_name='Name', db_index=True)),
                ('description', models.TextField(help_text='Organization Description', null=True, verbose_name='Description', blank=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'name', always_update=True, unique=True)),
                ('hashtag', models.CharField(max_length=80, blank=True, help_text='Hashtag', null=True, verbose_name='Hashtag', db_index=True)),
                ('website', models.URLField(blank=True, help_text='Organization Website', null=True, verbose_name='Website', db_index=True)),
                ('video', models.URLField(blank=True, help_text='Organization Informational Video', null=True, verbose_name='Video', db_index=True)),
                ('email', models.EmailField(max_length=254, blank=True, help_text='Organization Email', null=True, verbose_name='Email', db_index=True)),
                ('is_alt_person', models.BooleanField(default=False)),
                ('alt_person_fullname', models.CharField(help_text='Organization contact Person full Name', max_length=80, null=True, verbose_name='Full Name', blank=True)),
                ('alt_person_email', models.EmailField(help_text='Organization contact Person Email', max_length=80, null=True, verbose_name='Email', blank=True)),
                ('alt_person_phone', phonenumber_field.modelfields.PhoneNumberField(help_text='Organization contact Person Phone Number', max_length=128, verbose_name='Phone Number', blank=True)),
                ('is_newly_created', models.BooleanField(default=True)),
                ('is_hidden', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('address', models.ForeignKey(blank=True, to='core.Address', help_text='Organization Address', null=True, verbose_name='Address')),
                ('author', models.ForeignKey(related_name='created_organizations', verbose_name='Author', to=settings.AUTH_USER_MODEL, help_text='Organization Author')),
                ('phone_number', models.ForeignKey(blank=True, to='core.Phone', help_text='Organization Phone Numbers', null=True, verbose_name='Phone Numbers')),
                ('subscribers', models.ManyToManyField(help_text='Organization Subscribers', related_name='organization_subscribers', verbose_name='Subscribers', to=settings.AUTH_USER_MODEL, blank=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated List of Tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'organization',
                'verbose_name_plural': 'organizations',
            },
            bases=(core.models.AttachmentMixin, core.models.ViewMixin, core.models.CommentMixin, core.models.RatingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OrganizationGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(help_text='Organiztion Group Name', max_length=80, verbose_name='Name', db_index=True)),
                ('description', models.TextField(help_text='Organization Group Description', null=True, verbose_name='Description', blank=True)),
                ('author', models.ForeignKey(related_name='organization_group_author', verbose_name='Author', to=settings.AUTH_USER_MODEL, help_text='Organization Group Author')),
                ('members', models.ManyToManyField(help_text='Organization Group Member', related_name='organization_group_members', verbose_name='Group Member', to=settings.AUTH_USER_MODEL, blank=True)),
                ('organization', models.ForeignKey(related_name='organization_groups', verbose_name='Organization', to='organizations.Organization', help_text='Organization')),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'organization group',
                'verbose_name_plural': 'organization groups',
            },
            bases=(core.models.AttachmentMixin, core.models.ViewMixin, core.models.CommentMixin, core.models.RatingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OrganizationStaff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('position', models.CharField(max_length=200, blank=True, help_text='Position', null=True, verbose_name='Position', db_index=True)),
                ('bio', models.TextField(help_text='Short Bio', null=True, verbose_name='Bio', blank=True)),
                ('author', models.ForeignKey(related_name='organization_staff_members_created', verbose_name='Author', to=settings.AUTH_USER_MODEL, help_text='Organization Staff Member Author')),
                ('member', models.ForeignKey(related_name='organization_staff_member', blank=True, to=settings.AUTH_USER_MODEL, help_text='Organization Staff Member', null=True, verbose_name='Staff Member')),
                ('organization', models.ForeignKey(related_name='organization_staff_members', verbose_name='Organization', to='organizations.Organization', help_text='Organization')),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'organization staff member',
                'verbose_name_plural': 'organization staff members',
            },
            bases=(core.models.AttachmentMixin, core.models.ViewMixin, core.models.CommentMixin, core.models.RatingMixin, models.Model),
        ),
    ]
