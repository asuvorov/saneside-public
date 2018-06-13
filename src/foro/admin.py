from django.contrib import admin

from adminsortable2.admin import (
    SortableAdminMixin,
    SortableInlineAdminMixin,
    )
from mptt.admin import (
    MPTTModelAdmin,
    DraggableMPTTAdmin,
    )
from papertrail.admin import AdminEventLoggerMixin
from rangefilter.filter import (
    DateRangeFilter,
    DateTimeRangeFilter,
    )

from foro.models import (
    Section,
    Forum,
    Topic,
    Post,
    )


# -----------------------------------------------------------------------------
# --- SECTION ADMIN
# -----------------------------------------------------------------------------
class ForumInline(admin.TabularInline):
    """Forum Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = Forum


class SectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Section Admin."""

    list_display = [
        "id",
        "title", "order", "author",
        "created", "modified",
    ]
    list_display_links = [
        "title",
    ]
    list_filter = [
        "author",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "title", "author"
    ]
    inlines = [
        ForumInline,
    ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Docstring."""
        if db_field.name == "order":
            current_order_count = Section.objects.count()
            db_field.default = current_order_count

        return super(SectionAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)

admin.site.register(Section, SectionAdmin)


# -----------------------------------------------------------------------------
# --- FORUM ADMIN
# -----------------------------------------------------------------------------
class TopicInline(admin.TabularInline):
    """Topic Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = Topic


class ForumAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """Forum Admin."""

    list_display = [
        "id",
        "title", "description", "author",
        "created", "modified",
    ]
    list_display_links = [
        "title",
    ]
    list_filter = [
        "author",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "title", "description", "author"
    ]
    inlines = [
        TopicInline,
    ]

    papertrail_type_filters = {
        "Forum events": (
            "new-forum-created",
            "forum-edited",
        ),
    }

admin.site.register(Forum, ForumAdmin)


# -----------------------------------------------------------------------------
# --- TOPIC ADMIN
# -----------------------------------------------------------------------------
class PostInline(admin.TabularInline):
    """Post Inline."""

    classes = [
        "grp-collapse grp-closed",
    ]
    inline_classes = [
        "grp-collapse grp-closed",
    ]

    model = Post


class TopicAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """Topic Admin."""

    list_display = [
        "id",
        "title", "description", "forum", "author",
        "created", "modified",
    ]
    list_display_links = [
        "title",
    ]
    list_filter = [
        "forum", "author",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "title", "description", "forum", "author"
    ]
    inlines = [
        PostInline,
    ]

    papertrail_type_filters = {
        "Forum events": (
            "forum-topic-created",
            "forum-topic-edited",
        ),
    }

admin.site.register(Topic, TopicAdmin)


# -----------------------------------------------------------------------------
# --- POST ADMIN
# ------------------------------------------------------------------------------
class PostAdmin(AdminEventLoggerMixin, admin.ModelAdmin):
    """Post Admin."""

    list_display = [
        "id",
        "title", "topic", "author",
        "level", "lft", "rght", "tree_id",
        "created", "modified",
    ]
    list_display_links = [
        "title",
    ]
    list_filter = [
        "title", "topic", "author",
        ("created", DateRangeFilter),
        ("modified", DateRangeFilter),
    ]
    search_fields = [
        "title", "topic", "author",
    ]

    papertrail_type_filters = {
        "Forum events": (
            "forum-topic-post-created",
            "forum-topic-post-edited",
        ),
    }

# admin.site.register(Post, PostAdmin)
admin.site.register(
    Post,
    MPTTModelAdmin,
    search_fields=[
        "title", "author",
    ],
    list_display=[
        "id",
        "title", "topic", "author",
        "level", "lft", "rght", "tree_id",
        "created", "modified",
    ],
    list_display_links=[
        "title",
    ]
)
