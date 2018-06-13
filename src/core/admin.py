from django.contrib import admin

from rangefilter.filter import (
    DateRangeFilter,
    DateTimeRangeFilter,
    )

from core.models import (
    Address,
    AttachedDocument,
    AttachedImage,
    AttachedUrl,
    AttachedVideoUrl,
    Comment,
    Complaint,
    Newsletter,
    Phone,
    Rating,
    SocialLink,
    TemporaryFile,
    View,
    )


# -----------------------------------------------------------------------------
# --- ADDRESS ADMIN
# -----------------------------------------------------------------------------
class AddressAdmin(admin.ModelAdmin):
    """Address Admin."""

    fieldsets = (
        ("", {
            "classes":  (""),
            "fields":   (
                "address_1",
                "address_2",
                "city",
                ("zip_code", "province",),
                "country",
                "notes",
            ),
        }),
    )

    list_display = [
        "id",
        "address_1", "address_2", "city", "zip_code", "province", "country",
        "created", "modified",
    ]
    list_display_links = [
        "id",
    ]
    list_filter = [
        "zip_code", "country",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "zip_code", "country",
    ]

admin.site.register(Address, AddressAdmin)


# -----------------------------------------------------------------------------
# --- ATTACHMENTS ADMIN
# -----------------------------------------------------------------------------
class AttachedImageAdmin(admin.ModelAdmin):
    """Attahced Image Admin."""

    list_display = [
        "id",
        "name", "image", "content_object",
        "created", "modified",
    ]
    list_display_links = [
        "name",
    ]
    list_filter = []
    search_fields = [
        "name", "image", "content_object",
    ]

admin.site.register(AttachedImage, AttachedImageAdmin)


class AttachedDocumentAdmin(admin.ModelAdmin):
    """Attahced Document Admin."""

    list_display = [
        "id",
        "name", "document", "content_object",
        "created", "modified",
    ]
    list_display_links = [
        "name",
    ]
    list_filter = []
    search_fields = [
        "name", "document", "content_object",
    ]

admin.site.register(AttachedDocument, AttachedDocumentAdmin)


class AttachedUrlAdmin(admin.ModelAdmin):
    """Attahced URL Admin."""

    list_display = [
        "id",
        "url", "title", "content_object",
        "created", "modified",
    ]
    list_display_links = [
        "url",
    ]
    list_filter = []
    search_fields = [
        "url", "title", "content_object",
    ]

admin.site.register(AttachedUrl, AttachedUrlAdmin)


class AttachedVideoUrlAdmin(admin.ModelAdmin):
    """Attahced Video URL Admin."""

    list_display = [
        "id",
        "url", "content_object",
        "created", "modified",
    ]
    list_display_links = [
        "url",
    ]
    list_filter = []
    search_fields = [
        "url", "content_object",
    ]

admin.site.register(AttachedVideoUrl, AttachedVideoUrlAdmin)


# -----------------------------------------------------------------------------
# --- PHONE ADMIN
# -----------------------------------------------------------------------------
class PhoneAdmin(admin.ModelAdmin):
    """Phone Admin."""

    fieldsets = (
        ("", {
            "classes":  (""),
            "fields":   (
                ("phone_number", "phone_number_ext",),
                ("mobile_phone_number", "mobile_phone_number_ext",),
            ),
        }),
    )

    list_display = [
        "id",
        "phone_number", "mobile_phone_number",
        "created", "modified",
    ]
    list_display_links = [
        "id", "phone_number", "mobile_phone_number",
    ]
    list_filter = [
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "phone_number", "mobile_phone_number",
    ]

admin.site.register(Phone, PhoneAdmin)


# -----------------------------------------------------------------------------
# --- TEMPORARY FILE ADMIN
# -----------------------------------------------------------------------------
class TemporaryFileAdmin(admin.ModelAdmin):
    """Temporary File Admin."""

    list_display = [
        "id",
        "file", "name",
        "created", "modified",
    ]
    list_display_links = [
        "file", "name",
    ]
    list_filter = []
    search_fields = [
        "file", "name",
    ]

admin.site.register(TemporaryFile, TemporaryFileAdmin)


# -----------------------------------------------------------------------------
# --- VIEW ADMIN
# -----------------------------------------------------------------------------
class ViewAdmin(admin.ModelAdmin):
    """View Admin."""

    list_display = [
        "id",
        "user", "content_type", "object_id", "content_object",
        "created", "modified",
    ]
    list_display_links = [
        "id", "user",
    ]
    list_filter = [
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "user", "content_type",
    ]

admin.site.register(View, ViewAdmin)


# -----------------------------------------------------------------------------
# --- COMMENT ADMIN
# -----------------------------------------------------------------------------
class CommentAdmin(admin.ModelAdmin):
    """Comment Admin."""

    list_display = [
        "id",
        "user", "content_type", "object_id", "content_object",
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
        "user", "content_type",
    ]

admin.site.register(Comment, CommentAdmin)


# -----------------------------------------------------------------------------
# --- COMPLAINT ADMIN
# -----------------------------------------------------------------------------
def mark_as_processed(modeladmin, request, queryset):
    queryset.update(is_processed=True)

mark_as_processed.short_description = "Mark selected Complaints as processed"


def mark_as_deleted(modeladmin, request, queryset):
    queryset.update(is_deleted=True)

mark_as_deleted.short_description = "Mark selected Complaints as deleted"


class ComplaintAdmin(admin.ModelAdmin):
    """Complaint Admin."""

    list_display = [
        "id",
        "user", "content_type", "object_id", "content_object",
        "text",
        "is_processed", "is_deleted",
        "created", "modified",
    ]
    list_display_links = [
        "user",
    ]
    list_filter = [
        "is_processed", "is_deleted",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "user", "content_type",
    ]
    actions = [
        mark_as_processed,
        mark_as_deleted,
    ]

admin.site.register(Complaint, ComplaintAdmin)


# -----------------------------------------------------------------------------
# --- RATING ADMIN
# -----------------------------------------------------------------------------
class RatingAdmin(admin.ModelAdmin):
    """Rating Admin."""

    list_display = [
        "id",
        "author", "rating", "content_type", "object_id", "content_object",
        "created", "modified",
    ]
    list_display_links = [
        "id", "author",
    ]
    list_filter = [
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "author", "content_type",
    ]

admin.site.register(Rating, RatingAdmin)


# -----------------------------------------------------------------------------
# --- NEWSLETTER ADMIN
# -----------------------------------------------------------------------------
class NewsletterAdmin(admin.ModelAdmin):
    """Newsletter Admin."""

    list_display = [
        "id",
        "author", "title", "content_type", "object_id", "content_object",
        "created", "modified",
    ]
    list_display_links = [
        "author", "title",
    ]
    list_filter = [
        "author",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "author", "title", "content_type",
    ]

admin.site.register(Newsletter, NewsletterAdmin)


# -----------------------------------------------------------------------------
# --- SOCIAL LINK ADMIN
# -----------------------------------------------------------------------------
class SocialLinkAdmin(admin.ModelAdmin):
    """Social Link Admin."""

    list_display = [
        "id",
        "social_app", "url", "content_type", "object_id", "content_object",
        "created", "modified",
    ]
    list_display_links = [
        "id", "social_app", "url",
    ]
    list_filter = [
        "social_app",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "social_app", "url", "content_type",
    ]

admin.site.register(SocialLink, SocialLinkAdmin)
