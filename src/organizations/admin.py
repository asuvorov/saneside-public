from django.contrib import admin
from django.contrib.contenttypes import admin as ct_admin

from adminsortable2.admin import (
    SortableAdminMixin,
    SortableInlineAdminMixin,
    )
from papertrail.admin import AdminEventLoggerMixin
from rangefilter.filter import (
    DateRangeFilter,
    DateTimeRangeFilter,
    )

from challenges.models import Challenge
from core.models import SocialLink
from organizations.models import (
    Organization,
    OrganizationGroup,
    OrganizationStaff,
    )


# -----------------------------------------------------------------------------
# --- INLINES
# -----------------------------------------------------------------------------
class ChallengeInline(admin.TabularInline):
    """Challenge Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]
    exclude = [
        "avatar", "description", "hashtag",
        "addressless", "address",
        "month", "day_of_week", "day_of_month",
        "start_date", "start_time", "start_tz",
        "alt_person_fullname", "alt_person_email", "alt_person_phone",
        "closed_reason", "achievements", "is_newly_created",
        "allow_reenter", "accept_automatically", "acceptance_text",
    ]

    model = Challenge


class OrganizationStaffInline(SortableInlineAdminMixin, admin.TabularInline):
    """Organization Staff Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = OrganizationStaff


class OrganizationGroupInline(admin.TabularInline):
    """Organization Group Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = OrganizationGroup


class SocialLinkInline(ct_admin.GenericTabularInline):
    """Social Link Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = SocialLink


# -----------------------------------------------------------------------------
# --- ORGANIZATION ADMIN
# -----------------------------------------------------------------------------
class OrganizationAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """Organization Admin."""

    fieldsets = (
        ("", {
            "classes":  (""),
            "fields":   (
                "author",
                ("avatar", "image_tag",),
                "name",
                "description",
                "subscribers",
            ),
        }),
        ("Tags", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("tags", "hashtag",),
            ),
        }),
        ("Address & Phone Number", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("addressless", "address", "phone_number",),
            ),
        }),
        ("URLs", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("website", "video", "email",),
            ),
        }),
        ("Contact Person", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                "is_alt_person",
                ("alt_person_fullname", "alt_person_email", "alt_person_phone",),
            ),
        }),
        ("Flags", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("is_newly_created", "is_hidden", "is_deleted",),
            ),
        }),
    )

    list_display = [
        "id",
        "name", "image_tag", "author", "is_hidden", "is_deleted",
        "created", "modified",
    ]
    list_display_links = [
        "name",
    ]
    list_filter = [
        "author", "is_hidden", "is_deleted",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "name", "author",
    ]
    readonly_fields = [
        "image_tag",
    ]
    inlines = [
        ChallengeInline,
        OrganizationStaffInline,
        OrganizationGroupInline,
        SocialLinkInline,
    ]

    papertrail_type_filters = {
        "Organization events": (
            "new-organization-created",
            "organization-edited",
        ),
        "Invite Events": (
            "invite-created",
            "invite-accepted",
            "invite-rejected",
            "invite-revoked",
        ),
        "Complaint Events": (
            "complaint-created",
            "complaint-processed",
            "complaint-deleted",
        ),
    }

admin.site.register(Organization, OrganizationAdmin)


# -----------------------------------------------------------------------------
# --- ORGANIZATION STAFF ADMIN
# -----------------------------------------------------------------------------
class OrganizationStaffAdmin(admin.ModelAdmin):
    """Organization Staff Admin."""

    list_display = [
        "member", "organization", "author", "order",
        "created", "modified",
    ]
    list_filter = [
        "member", "organization", "author",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "member",
    ]

admin.site.register(OrganizationStaff, OrganizationStaffAdmin)


# -----------------------------------------------------------------------------
# --- ORGANIZATION GROUP ADMIN
# -----------------------------------------------------------------------------
class OrganizationGroupAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """Organization Group Admin."""

    list_display = [
        "name", "organization", "author",
        "created", "modified",
    ]
    list_filter = [
        "name", "organization", "author",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "name",
    ]

    papertrail_type_filters = {
        "Invite Events": (
            "invite-created",
            "invite-accepted",
            "invite-rejected",
            "invite-revoked",
        ),
    }

admin.site.register(OrganizationGroup, OrganizationGroupAdmin)
