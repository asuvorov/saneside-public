# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields
import core.models
from django.conf import settings
import taggit.managers
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('avatar', models.ImageField(upload_to=b'images/challenges/avatars')),
                ('title', models.CharField(help_text='Post Title', max_length=80, verbose_name='Title', db_index=True)),
                ('content', models.TextField(help_text='Post Content', null=True, verbose_name='Content', blank=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'title', always_update=True, unique=True)),
                ('hashtag', models.CharField(max_length=80, blank=True, help_text='Hashtag', null=True, verbose_name='Hashtag', db_index=True)),
                ('status', models.CharField(default=b'0', help_text='Post Status', max_length=2, verbose_name='Status', choices=[(b'0', 'Draft'), (b'1', 'Visible'), (b'2', 'Closed')])),
                ('author', models.ForeignKey(related_name='posted_posts', verbose_name='Post Author', to=settings.AUTH_USER_MODEL, help_text='Post Author')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated List of Tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
            },
            bases=(core.models.ViewMixin, core.models.CommentMixin, core.models.RatingMixin, models.Model),
        ),
    ]
