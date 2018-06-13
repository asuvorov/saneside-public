from django.contrib import admin

from papertrail.admin import AdminEventLoggerMixin
from rangefilter.filter import (
    DateRangeFilter,
    DateTimeRangeFilter,
    )

from invites.models import Invite


# -----------------------------------------------------------------------------
# --- INVITE ADMIN
# -----------------------------------------------------------------------------
class InviteAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """Invite Admin."""

    fieldsets = (
        ("", {
            "classes":  (""),
            "fields":   (
                "inviter",
                "invitee",
                "status",
                ("content_type", "object_id"),
            ),
        }),
        ("Significant Texts", {
            "classes":  (
                "grp-collapse grp-closed",
            ),
            "fields":   (
                "invitation_text",
                "rejection_text",
            ),
        }),
        ("Significant Dates", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("date_accepted", "date_rejected", "date_revoked"),
            ),
        }),
        ("Flags", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("is_archived_for_inviter", "is_archived_for_invitee"),
            ),
        }),
    )

    list_display = [
        "id",
        "inviter", "invitee", "content_object", "status",
        "created", "modified",
    ]
    list_display_links = [
        "inviter", "invitee",
    ]
    list_filter = [
        "status",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "inviter", "invitee", "content_object", "status",
    ]

    papertrail_type_filters = {
        "Invite Events": (
            "invite-created",
            "invite-accepted",
            "invite-rejected",
            "invite-revoked",
        ),
    }

admin.site.register(Invite, InviteAdmin)
