# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('status', models.CharField(default=b'0', choices=[(b'0', 'New'), (b'1', 'Accepted'), (b'2', 'Rejected'), (b'4', 'Revoked')], max_length=2, help_text='Invite Status', verbose_name='Status', db_index=True)),
                ('object_id', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('invitation_text', models.TextField(help_text='Invitation Text', null=True, verbose_name='Invitation Text', blank=True)),
                ('rejection_text', models.TextField(help_text='Rejection', null=True, verbose_name='Rejection Text', blank=True)),
                ('date_accepted', models.DateField(help_text='Date accepted', null=True, verbose_name='Date accepted', db_index=True, blank=True)),
                ('date_rejected', models.DateField(help_text='Date rejected', null=True, verbose_name='Date rejected', db_index=True, blank=True)),
                ('date_revoked', models.DateField(help_text='Date revoked', null=True, verbose_name='Date revoked', db_index=True, blank=True)),
                ('content_type', models.ForeignKey(default=None, blank=True, to='contenttypes.ContentType', null=True)),
                ('invitee', models.ForeignKey(related_name='invitee', verbose_name='Invitee', to=settings.AUTH_USER_MODEL, help_text='Invitee')),
                ('inviter', models.ForeignKey(related_name='inviter', verbose_name='Inviter', to=settings.AUTH_USER_MODEL, help_text='Inviter')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'invite',
                'verbose_name_plural': 'invites',
            },
        ),
    ]
