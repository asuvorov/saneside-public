from django.contrib import admin
from django.contrib.contenttypes import admin as ct_admin

from papertrail.admin import AdminEventLoggerMixin
from rangefilter.filter import (
    DateRangeFilter,
    DateTimeRangeFilter,
    )

from core.models import (
    Comment,
    Complaint,
    SocialLink,
    )
from challenges.models import (
    Category,
    Challenge,
    Participation,
    Role,
    )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ CHALLENGE CATEGORY ADMIN
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# -----------------------------------------------------------------------------
# --- INLINES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# --- CHALLENGE ADMIN
# -----------------------------------------------------------------------------
class CategoryAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """Challenge Category Admin."""

    fieldsets = (
        ("", {
            "classes":  (""),
            "fields":   (
                ("avatar", "image_tag"),
                "name",
                "description",
                "category",
                ("color", "icon", "image"),
            ),
        }),
    )

    list_display = [
        "id",
        "name", "avatar", "image_tag",
        "category", "color", "icon", "image",
        "created", "modified",
    ]
    list_display_links = [
        "name",
    ]
    list_filter = []
    search_fields = [
        "name",
    ]
    readonly_fields = [
        "image_tag",
    ]
    inlines = []

admin.site.register(Category, CategoryAdmin)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ CHALLENGE ADMIN
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# -----------------------------------------------------------------------------
# --- INLINES
# -----------------------------------------------------------------------------
class ParticipationInline(admin.TabularInline):
    """Participation Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]
    exclude = [
        "application_text", "cancellation_text",
        "selfreflection_activity_text", "selfreflection_learning_text",
        "selfreflection_rejection_text", "acknowledgement_text",
    ]

    model = Participation


class RoleInline(admin.TabularInline):
    """Role Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = Role


class CommentInline(ct_admin.GenericTabularInline):
    """Comment Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = Comment


class ComplaintInline(ct_admin.GenericTabularInline):
    """Complaint Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = Complaint


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
# --- CHALLENGE ADMIN
# -----------------------------------------------------------------------------
class ChallengeAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """Challenge Admin."""

    fieldsets = (
        ("", {
            "classes":  (""),
            "fields":   (
                "author",
                ("avatar", "image_tag"),
                "challenge_url",
                "name",
                "description",
                "category",
                ("status", "application"),
                "duration",
                "organization",
                "achievements",
                "closed_reason",
            ),
        }),
        ("Tags", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("tags", "hashtag"),
            ),
        }),
        ("Location", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("addressless", "address"),
            ),
        }),
        ("Recurrence", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                "recurrence",
        #         ("month", "day_of_week", "day_of_month"),
            ),
        }),
        ("Start Date/Time", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("start_date", "start_time", "start_tz", "start_date_time_tz"),
            ),
        }),
        ("Contact Person", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                "is_alt_person",
                ("alt_person_fullname", "alt_person_email", "alt_person_phone"),
            ),
        }),
        ("Flags", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                "is_newly_created",
                "allow_reenter",
                ("accept_automatically", "acceptance_text",),
            ),
        }),
    )

    list_display = [
        "id",
        "name", "image_tag", "status", "challenge_url",
        "start_date", "start_time", "start_tz",
        "organization", "application", "author",
        "created", "modified",
    ]
    list_display_links = [
        "name",
    ]
    list_filter = [
        "status", "organization", "application", "author",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "name", "organization",
    ]
    readonly_fields = [
        "image_tag", "challenge_url",
    ]
    inlines = [
        RoleInline,
        SocialLinkInline,
        CommentInline,
        ComplaintInline,
        ParticipationInline,
    ]

    papertrail_type_filters = {
        "Challenge Events": (
            "new-challenge-created",
            "challenge-edited",
            "challenge-published",
            "challenge-completed",
            "challenge-closed",
        ),
        "Participation Events": (
            "user-challenge-signed-up",
            "user-participation-withdrew",
            "user-participation-removed",
            "user-participation-accepted",
            "user-participation-rejected",
            "user-selfreflection-submitted",
            "user-selfreflection-accepted",
            "user-selfreflection-rejected",
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

admin.site.register(Challenge, ChallengeAdmin)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ PARTICIPATION ADMIN
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ParticipationAdmin(admin.ModelAdmin):
    """Participation Admin."""

    fieldsets = (
        ("", {
            "classes":  (""),
            "fields":   (
                ("user", "image_tag",),
                "challenge",
                "role",
                "status",
            ),
        }),
        ("Significant Texts", {
            "classes":  (
                "grp-collapse grp-closed",
            ),
            "fields":   (
                "application_text",
                "cancellation_text",
                "selfreflection_activity_text",
                "selfreflection_learning_text",
                "selfreflection_rejection_text",
                "acknowledgement_text",
            ),
        }),
        ("Significant Dates", {
            "classes":  (
                "grp-collapse grp-closed",
            ),
            "fields":   (
                "date_accepted",
                "date_cancelled",
                "date_selfreflection",
                "date_selfreflection_rejection",
                "date_acknowledged",
            ),
        }),
    )

    list_display = [
        "id",
        "user", "image_tag", "challenge", "role", "status",
    ]
    list_display_links = [
        "user",
    ]
    list_filter = [
        "status",
    ]
    search_fields = [
        "user", "challenge",
    ]
    readonly_fields = [
        "image_tag",
    ]

admin.site.register(Participation, ParticipationAdmin)
