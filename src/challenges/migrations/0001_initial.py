# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields
import core.models
from django.conf import settings
import phonenumber_field.modelfields
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('avatar', models.ImageField(upload_to=b'images/challenges/avatars')),
                ('name', models.CharField(help_text='Challenge Name', max_length=80, verbose_name='Name', db_index=True)),
                ('description', models.TextField(help_text='Challenge Description', null=True, verbose_name='Description', blank=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'name', always_update=True, unique=True)),
                ('hashtag', models.CharField(max_length=80, blank=True, help_text='Hashtag', null=True, verbose_name='Hashtag', db_index=True)),
                ('category', models.CharField(choices=[(b'0', 'Animals'), (b'1', 'Arts & Culture'), (b'2', 'Children & Youth'), (b'4', 'Community'), (b'8', 'Education & Literacy'), (b'16', 'Environment'), (b'32', 'Health & Medicine'), (b'64', 'Sports & Recreation'), (b'128', 'Veterans & Seniors')], max_length=4, blank=True, help_text='Challenge Category', null=True, verbose_name='Category')),
                ('status', models.CharField(default=b'1', help_text='Challenge Status', max_length=2, verbose_name='Status', choices=[(b'0', 'Draft'), (b'1', 'Upcoming'), (b'2', 'Complete'), (b'4', 'Expired'), (b'8', 'Closed')])),
                ('application', models.CharField(default=b'0', help_text='Challenge Application', max_length=2, verbose_name='Application', choices=[(b'0', 'Anyone can participate.'), (b'1', 'Participate only after a confirmed Application')])),
                ('duration', models.PositiveIntegerField(default=1, help_text='Challenge Duration', verbose_name='Duration')),
                ('start_date', models.DateField(help_text='Challenge Start Date', verbose_name='Start Date', db_index=True)),
                ('start_time', models.TimeField(help_text='Challenge Start Time', verbose_name='Start Time', db_index=True)),
                ('is_alt_person', models.BooleanField(default=False)),
                ('alt_person_fullname', models.CharField(help_text='Challenge Contact Person full Name', max_length=80, null=True, verbose_name='Full Name', blank=True)),
                ('alt_person_email', models.EmailField(help_text='Challenge Contact Person Email', max_length=80, null=True, verbose_name='Email', blank=True)),
                ('alt_person_phone', phonenumber_field.modelfields.PhoneNumberField(help_text='Challenge Contact Person Phone Numbers', max_length=128, null=True, verbose_name='Phone Number', blank=True)),
                ('closed_reason', models.TextField(help_text='Reason for closing', null=True, verbose_name='Reason for closing', blank=True)),
                ('is_newly_created', models.BooleanField(default=True)),
                ('allow_reenter', models.BooleanField(default=True, help_text='Allow Members to apply again to the Challenge after withdrawing their Application.', verbose_name='Allow Members to apply again to the Challenge after withdrawing their Application.')),
                ('accept_automatically', models.BooleanField(default=False, help_text="Automatically accept Participants' Experience Reports after the Challenge completed.", verbose_name="Automatically accept Participants' Experience Reports after the Challenge completed.")),
                ('acceptance_text', models.TextField(default='Great Job', help_text='This Text will automatically appear as an Acknowledgment Text for each Participant after Challenge has been marked as completed.', null=True, verbose_name='Acceptance Text', blank=True)),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'challenge',
                'verbose_name_plural': 'challenges',
            },
            bases=(core.models.AttachmentMixin, core.models.ViewMixin, core.models.CommentMixin, core.models.RatingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'0', help_text='Participation Status', max_length=2, verbose_name='Status', choices=[(b'0', 'Waiting for Confirmation'), (b'1', 'You were not accepted to this Challenge'), (b'2', 'Signed up'), (b'4', 'The Organizer removed you from this Challenge'), (b'8', 'You withdrew your Participation to this Challenge'), (b'16', 'Please write your Experience Report'), (b'32', 'Waiting for Acknowledgment'), (b'64', 'Report acknowledged')])),
                ('application_text', models.TextField(help_text='Application Text', null=True, verbose_name='Application Text', blank=True)),
                ('cancellation_text', models.TextField(help_text='Cancellation Text', null=True, verbose_name='Cancellation Text', blank=True)),
                ('selfreflection_activity_text', models.TextField(help_text='Experience Report - Activity Text', null=True, verbose_name='Experience Report - Activity Text', blank=True)),
                ('selfreflection_learning_text', models.TextField(help_text='Experience Report - learning Text', null=True, verbose_name='Experience Report - learning Text', blank=True)),
                ('selfreflection_rejection_text', models.TextField(help_text='Experience Report - Rejection Text', null=True, verbose_name='Experience Report - Rejection Text', blank=True)),
                ('acknowledgement_text', models.TextField(help_text='Acknowledgement Text', null=True, verbose_name='Acknowledgement Text', blank=True)),
                ('date_created', models.DateField(auto_now_add=True, help_text='Date created', verbose_name='Date created', db_index=True)),
                ('date_accepted', models.DateField(help_text='Date accepted', null=True, verbose_name='Date accepted', db_index=True, blank=True)),
                ('date_cancelled', models.DateField(help_text='Date canceled', null=True, verbose_name='Date canceled', db_index=True, blank=True)),
                ('date_selfreflection', models.DateField(help_text='Date of receiving of the Experience Report', null=True, verbose_name='Date of the Experience Report', db_index=True, blank=True)),
                ('date_selfreflection_rejection', models.DateField(help_text='Date of Rejection of the Experience Report', null=True, verbose_name='Date of the Experience Report Rejection', db_index=True, blank=True)),
                ('date_acknowledged', models.DateField(help_text='Date of acknowledging of the Experience Report', null=True, verbose_name='Date acknowledged', db_index=True, blank=True)),
                ('challenge', models.ForeignKey(related_name='challenge_participations', verbose_name='Challenge', to='challenges.Challenge', help_text='Challenge')),
            ],
            options={
                'ordering': ['-date_created'],
                'verbose_name': 'participation',
                'verbose_name_plural': 'participations',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(help_text='Role Name', max_length=80, verbose_name='Name', db_index=True)),
                ('quantity', models.PositiveIntegerField(help_text='Quantity', verbose_name='Quantity')),
                ('challenge', models.ForeignKey(related_name='challenge_roles', verbose_name='Challenge', to='challenges.Challenge', help_text='Challenge')),
            ],
            options={
                'ordering': ['created'],
                'verbose_name': 'role',
                'verbose_name_plural': 'roles',
            },
        ),
        migrations.AddField(
            model_name='participation',
            name='role',
            field=models.ForeignKey(related_name='role_participations', blank=True, to='challenges.Role', help_text='Role, if applicable', null=True, verbose_name='Role'),
        ),
        migrations.AddField(
            model_name='participation',
            name='user',
            field=models.ForeignKey(related_name='user_participations', verbose_name='User', to=settings.AUTH_USER_MODEL, help_text='Participant'),
        ),
    ]
