# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields
from django.conf import settings
import phonenumber_field.modelfields
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('address_1', models.CharField(max_length=80, blank=True, help_text='Address Line 1', null=True, verbose_name='Address 1', db_index=True)),
                ('address_2', models.CharField(max_length=80, blank=True, help_text='Adderss Line 2', null=True, verbose_name='Address 2', db_index=True)),
                ('city', models.CharField(max_length=80, blank=True, help_text='City', null=True, verbose_name='City', db_index=True)),
                ('zip_code', models.PositiveIntegerField(help_text='Zip/Postal Code', null=True, verbose_name='Zip/Postal Code', db_index=True, blank=True)),
                ('province', models.CharField(max_length=80, blank=True, help_text='State/Province', null=True, verbose_name='State/Province', db_index=True)),
                ('country', django_countries.fields.CountryField(help_text='Country', max_length=2, verbose_name='Country', db_index=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'address',
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='AttachedDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=255, blank=True, help_text='File Name', null=True, verbose_name='Name', db_index=True)),
                ('document', models.FileField(upload_to=b'documents')),
                ('object_id', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(default=None, blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'attached document',
                'verbose_name_plural': 'attached documents',
            },
        ),
        migrations.CreateModel(
            name='AttachedImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=255, blank=True, help_text='File Name', null=True, verbose_name='Name', db_index=True)),
                ('image', models.ImageField(upload_to=b'images')),
                ('object_id', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(default=None, blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'attached image',
                'verbose_name_plural': 'attached images',
            },
        ),
        migrations.CreateModel(
            name='AttachedVideoUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('url', models.URLField()),
                ('object_id', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(default=None, blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'attached video url',
                'verbose_name_plural': 'attached video urls',
            },
        ),
        migrations.CreateModel(
            name='AtttachedUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('url', models.URLField()),
                ('title', models.CharField(max_length=255, blank=True, help_text='URL Title', null=True, verbose_name='Title', db_index=True)),
                ('object_id', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(default=None, blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'attached url',
                'verbose_name_plural': 'attached urls',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('text', models.TextField(help_text='Comment Text', verbose_name=b'Text')),
                ('object_id', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(default=None, blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created'],
                'verbose_name': 'commment',
                'verbose_name_plural': 'comments',
            },
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(help_text='Newsletter Title', max_length=80, verbose_name='Title', db_index=True)),
                ('content', models.TextField(help_text='Newsletter Content', null=True, verbose_name='Content', blank=True)),
                ('object_id', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('author', models.ForeignKey(related_name='sent_newsletters', verbose_name='Author', to=settings.AUTH_USER_MODEL, help_text='Newsletter Author')),
                ('content_type', models.ForeignKey(default=None, blank=True, to='contenttypes.ContentType', null=True)),
                ('recipients', models.ManyToManyField(related_name='newsletter_recipients', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'newsletter',
                'verbose_name_plural': 'newsletters',
            },
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, blank=True, help_text='Phone Number', null=True, verbose_name='Phone Number', db_index=True)),
                ('mobile_phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, blank=True, help_text='Mobile Phone Number', null=True, verbose_name='Mobile Phone Number', db_index=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'phone number',
                'verbose_name_plural': 'phone numbers',
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('rating', models.PositiveIntegerField(default=0, db_index=True)),
                ('review_text', models.TextField(help_text='Review Text', null=True, verbose_name='Review Text', blank=True)),
                ('object_id', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(default=None, blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'rating',
                'verbose_name_plural': 'ratings',
            },
        ),
        migrations.CreateModel(
            name='TemporaryFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('file', models.FileField(upload_to=b'tmp')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'temporary file',
                'verbose_name_plural': 'temporary files',
            },
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('object_id', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(default=None, blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'view',
                'verbose_name_plural': 'views',
            },
        ),
    ]
