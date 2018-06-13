from django.contrib import admin

from adminsortable2.admin import (
    SortableAdminMixin,
    SortableInlineAdminMixin,
    )
from papertrail.admin import AdminEventLoggerMixin
from rangefilter.filter import (
    DateRangeFilter,
    DateTimeRangeFilter,
    )

from accounts.models import (
    Team,
    TeamMember,
    UserLogin,
    UserPrivacyGeneral,
    UserPrivacyMembers,
    UserPrivacyAdmins,
    UserProfile,
    )


# -----------------------------------------------------------------------------
# --- USER PROFILE ADMIN
# -----------------------------------------------------------------------------
class UserProfileAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """User Profile Admin."""

    fieldsets = (
        ("", {
            "classes":  (""),
            "fields":   (
                "user",
                ("avatar", "image_tag",),
                "nickname",
                "bio",
                ("gender", "birth_day",),
            ),
        }),
        ("Address & Phone #", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                ("address", "phone_number",),
            ),
        }),
        ("Flags", {
            "classes":  (
                "grp-collapse grp-open",
            ),
            "fields":   (
                "receive_newsletters",
                "is_newly_created",
            ),
        }),
    )

    list_display = [
        "id",
        "user", "image_tag",
        "is_newly_created",
        "created", "modified",
    ]
    list_display_links = [
        "user",
    ]
    list_filter = [
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "user",
    ]
    readonly_fields = [
        "image_tag",
    ]

    papertrail_type_filters = {
        "Account Events": (
            "new-user-signed-up",
            "new-user-sign-up-confirmed",
            "user-logged-in",
        ),
        "Account Exceptions": (
            "exception-create-user-privacy",
        ),
        "Profile Events": (
            "user-profile-save-failed",
            "user-profile-privacy-save-failed",
        ),
        "Complaint Events": (
            "complaint-created",
            "complaint-processed",
            "complaint-deleted",
        ),
    }

admin.site.register(UserProfile, UserProfileAdmin)


# -----------------------------------------------------------------------------
# --- USER PROFILE PRIVACY
# -----------------------------------------------------------------------------
class UserPrivacyGeneralAdmin(admin.ModelAdmin):
    """User Profile Privacy General."""

    list_display = [
        "id",
        "user",
        "created", "modified",
    ]
    list_display_links = [
        "user",
    ]
    list_filter = [
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "user",
    ]

admin.site.register(UserPrivacyGeneral, UserPrivacyGeneralAdmin)


class UserPrivacyMembersAdmin(admin.ModelAdmin):
    """User Profile Privacy Members."""

    list_display = [
        "id",
        "user",
        "created", "modified",
    ]
    list_display_links = [
        "user",
    ]
    list_filter = [
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "user",
    ]

admin.site.register(UserPrivacyMembers, UserPrivacyMembersAdmin)


class UserPrivacyAdminsAdmin(admin.ModelAdmin):
    """User Profile Privacy Admins."""

    list_display = [
        "id",
        "user",
        "created", "modified",
    ]
    list_display_links = [
        "user",
    ]
    list_filter = [
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "user",
    ]

admin.site.register(UserPrivacyAdmins, UserPrivacyAdminsAdmin)


# -----------------------------------------------------------------------------
# --- USER LOGIN ADMIN
# -----------------------------------------------------------------------------
class UserLoginAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """User Login Admin."""

    list_display = [
        "id",
        "user", "ip", "provider", "country", "city",
        "created", "modified",
    ]
    list_display_links = [
        "user",
    ]
    list_filter = [
        "provider", "country", "city",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "user", "ip", "provider", "country", "city",
    ]

    papertrail_type_filters = {
        "User Login Exceptions": (
            "exception-insert-user-login",
            "exception-forgot-password-notify",
        ),
    }

admin.site.register(UserLogin, UserLoginAdmin)


# -----------------------------------------------------------------------------
# --- TEAM ADMIN
# -----------------------------------------------------------------------------
class TeamMemberInline(SortableInlineAdminMixin, admin.TabularInline):
    """Team Member Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = TeamMember


class TeamAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Team Admin."""

    list_display = [
        "id",
        "name", "order",
        "created", "modified",
    ]
    list_display_links = [
        "name",
    ]
    list_filter = [
        "name", "order",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "name",
    ]
    inlines = [
        TeamMemberInline,
    ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Docstring."""
        if db_field.name == "order":
            current_order_count = Team.objects.count()
            db_field.default = current_order_count

        return super(TeamAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)

admin.site.register(Team, TeamAdmin)


# -----------------------------------------------------------------------------
# -- TEAM MEMBER ADMIN
# -----------------------------------------------------------------------------
class TeamMemberAdmin(admin.ModelAdmin):
    """Team Member Admin."""

    fieldsets = (
        ("", {
            "classes":  (""),
            "fields":   (
                ("user", "image_tag",),
                "team",
                "position",
                "order",
            ),
        }),
    )

    list_display = [
        "id",
        "user", "image_tag", "position", "order", "team",
        "created", "modified",
    ]
    list_display_links = [
        "user",
    ]
    list_filter = [
        "team",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "user", "position", "team",
    ]
    readonly_fields = [
        "image_tag",
    ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Docstring."""
        if db_field.name == "order":
            current_order_count = TeamMember.objects.count()
            db_field.default = current_order_count

        return super(TeamMemberAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)

admin.site.register(TeamMember, TeamMemberAdmin)
