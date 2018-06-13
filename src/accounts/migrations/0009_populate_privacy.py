# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import migrations

from accounts.models import (
    UserPrivacyGeneral,
    UserPrivacyMembers,
    UserPrivacyAdmins,
    )


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return

    for user in User.objects.all():
        # ---------------------------------------------------------------------
        # --- Get or create User's Privacy Settings
        privacy_general, created = UserPrivacyGeneral.objects.get_or_create(
            user=user,
            )
        privacy_members, created = UserPrivacyMembers.objects.get_or_create(
            user=user,
            )
        privacy_admins, created = UserPrivacyAdmins.objects.get_or_create(
            user=user,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_remove_userprofile_privacy_mode'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
