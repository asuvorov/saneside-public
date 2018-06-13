import inspect

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import ping_google
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django_extensions.db.models import TimeStampedModel
from mptt.models import (
    MPTTModel,
    TreeForeignKey,
    )
from termcolor import colored

from app.utils import update_seo_model_instance_metadata
from core.decorators import autoconnect


# -----------------------------------------------------------------------------
# --- SECTION
# -----------------------------------------------------------------------------
class SectionManager(models.Manager):
    """Section Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(SectionManager, self).get_queryset()


@autoconnect
class Section(TimeStampedModel):
    """Section Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="authored_forum_sections",
        null=True, blank=True,
        verbose_name=_("Author"),
        help_text=_("Section Author"))

    title = models.CharField(
        db_index=True,
        max_length=60,
        verbose_name=_("Title"),
        help_text=_("Section Title"))
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Section Order (auto-incremented)"))

    objects = SectionManager()

    class Meta:
        verbose_name = _("section")
        verbose_name_plural = _("sections")
        ordering = ["order", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.title)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.title

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Signals
    def pre_save(self, **kwargs):
        """Docstring."""
        if not self.created:
            self.created = timezone.now()

        self.modified = timezone.now()

    def post_save(self, created, **kwargs):
        """Docstring."""
        pass

    def pre_delete(self, **kwargs):
        """Docstring."""
        pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass


# -----------------------------------------------------------------------------
# --- FORUM
# -----------------------------------------------------------------------------
class ForumManager(models.Manager):
    """Forum Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(ForumManager, self).get_queryset()


@autoconnect
class Forum(TimeStampedModel):
    """Forum Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="authored_forums",
        null=True, blank=True,
        verbose_name=_("Author"),
        help_text=_("Forum Author"))
    section = models.ForeignKey(
        Section,
        db_index=True,
        related_name="related_forums",
        verbose_name=_("Section"),
        help_text=_("Forum Section"))

    title = models.CharField(
        db_index=True,
        max_length=60,
        verbose_name=_("Title"),
        help_text=_("Forum Title"))
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("Description"),
        help_text=_("Forum Description"))
    style_css = models.TextField(
        null=True, blank=True,
        verbose_name=_("Style CSS"),
        help_text=_(
            "Forum Style CSS, e.g. <i class='fa fa-fw fa-4x fa-user'></i>"))

    slug = AutoSlugField(
        populate_from="title", unique=True, always_update=False)

    objects = ForumManager()

    class Meta:
        verbose_name = _("forum")
        verbose_name_plural = _("forums")
        ordering = ["-created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.title)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.title

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Forum direct URL
    def public_url(self, request=None):
        """Docstring."""
        if request:
            DOMAIN_NAME = request.get_host()
        else:
            DOMAIN_NAME = settings.DOMAIN_NAME

        url = reverse(
            "topic-list", kwargs={
                "forum_id":     self.id,
            })
        forum_link = u"http://{domain}{url}".format(
            domain=DOMAIN_NAME,
            url=url,
            )

        return forum_link

    def get_absolute_url(self):
        """Method to be called by Django Sitemap Framework."""
        url = reverse(
            "topic-list", kwargs={
                "forum_id":     self.id,
            })

        return url

    # -------------------------------------------------------------------------
    # --- Helpers
    def num_topics(self):
        """Docstring."""
        return self.related_topics.count()

    def num_posts(self):
        """Docstring."""
        return sum([t.num_posts() for t in self.related_topics.all()])

    def last_post(self):
        """Docstring."""
        if self.related_topics.count():
            last = None

            for t in self.related_topics.all():
                l = t.last_post()
                if l:
                    if not last:
                        last = l
                    elif l.created > last.created:
                        last = l

            return last

        return None

    # -------------------------------------------------------------------------
    # --- Signals
    def pre_save(self, **kwargs):
        """Docstring."""
        pass

    def post_save(self, created, **kwargs):
        """Docstring."""
        # ---------------------------------------------------------------------
        # --- Ping Google
        try:
            ping_google()
        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

        # ---------------------------------------------------------------------
        # --- Update/insert SEO Model Instance Metadata
        update_seo_model_instance_metadata(
            title=self.title,
            description=self.description,
            keywords=self.section.title,
            heading=self.title,
            path=self.get_absolute_url(),
            object_id=self.id,
            content_type_id=ContentType.objects.get_for_model(self).id,
        )

    def pre_delete(self, **kwargs):
        """Docstring."""
        pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass


# -----------------------------------------------------------------------------
# --- TOPIC
# -----------------------------------------------------------------------------
class TopicManager(models.Manager):
    """Topic Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(TopicManager, self).get_queryset()


@autoconnect
class Topic(TimeStampedModel):
    """Topic Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="authored_forum_topics",
        null=True, blank=True,
        verbose_name=_("Author"),
        help_text=_("Topic Author"))
    forum = models.ForeignKey(
        Forum,
        db_index=True,
        related_name="related_topics",
        verbose_name=_("Forum"),
        help_text=_("Forum"))

    title = models.CharField(
        db_index=True,
        max_length=60,
        verbose_name=_("Title"),
        help_text=_("Topic Title"))
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("Description"),
        help_text=_("Topic Description"))

    slug = AutoSlugField(
        populate_from="title", unique=True, always_update=False)

    objects = TopicManager()

    class Meta:
        verbose_name = _("forum topic")
        verbose_name_plural = _("forum topics")
        ordering = ["-created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s' in '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.title,
            self.forum.title)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.title

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    def public_url(self, request=None):
        """Docstring."""
        if request:
            DOMAIN_NAME = request.get_host()
        else:
            DOMAIN_NAME = settings.DOMAIN_NAME

        url = reverse(
            "topic-post-list", kwargs={
                "forum_id":     self.forum_id,
                "topic_id":     self.id,
            })
        forum_link = u"http://{domain}{url}".format(
            domain=DOMAIN_NAME,
            url=url,
            )

        return forum_link

    def get_absolute_url(self):
        """Method to be called by Django Sitemap Framework."""
        url = reverse(
            "topic-post-list", kwargs={
                "forum_id":     self.forum_id,
                "topic_id":     self.id,
            })

        return url

    # -------------------------------------------------------------------------
    # --- Helpers
    def num_posts(self):
        """Docstring."""
        return self.related_posts.count()

    def last_post(self):
        """Docstring."""
        if self.related_posts.count():
            return self.related_posts.order_by("-created")[0]

        return None

    # -------------------------------------------------------------------------
    # --- Signals
    def pre_save(self, **kwargs):
        """Docstring."""
        pass

    def post_save(self, created, **kwargs):
        """Docstring."""
        # ---------------------------------------------------------------------
        # --- Ping Google
        try:
            ping_google()
        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

        # ---------------------------------------------------------------------
        # --- Update/insert SEO Model Instance Metadata
        update_seo_model_instance_metadata(
            title=self.title,
            description=self.description,
            keywords=self.forum.title,
            heading=self.title,
            path=self.get_absolute_url(),
            object_id=self.id,
            content_type_id=ContentType.objects.get_for_model(self).id,
        )

    def pre_delete(self, **kwargs):
        """Docstring."""
        pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass


# -----------------------------------------------------------------------------
# --- POST
# -----------------------------------------------------------------------------
class PostManager(models.Manager):
    """Post Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(PostManager, self).get_queryset()


@autoconnect
class Post(MPTTModel, TimeStampedModel):
    """Post Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="authored_forum_posts",
        null=True, blank=True,
        verbose_name=_("Author"),
        help_text=_("Post Author"))
    topic = models.ForeignKey(
        Topic,
        db_index=True,
        related_name="related_posts",
        null=True, blank=True,
        verbose_name=_("Topic"),
        help_text=_("Post Topic"))

    parent = TreeForeignKey(
        "self",
        db_index=True,
        related_name="children",
        null=True, blank=True)

    title = models.CharField(
        db_index=True,
        max_length=60,
        verbose_name=_("Title"),
        help_text=_("Post Title"))
    body = RichTextUploadingField(
        config_name="awesome_ckeditor",
        max_length=10000, null=True, blank=True,
        verbose_name=_("Content"),
        help_text=_("Post Content"))

    slug = AutoSlugField(
        populate_from="title", unique=True, always_update=False)

    objects = PostManager()

    class Meta:
        verbose_name = _("forum topic post")
        verbose_name_plural = _("forum topic posts")
        ordering = ["-created", ]

    class MPTTMeta:
        order_insertion_by = ["title", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s' in '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.title,
            self.topic.title)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.title

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    def short(self):
        """Docstring."""
        return u"%s - %s\n%s" % (
            self.author, self.title, self.created.strftime("%b %d, %I:%M %p"))

    short.allow_tags = True

    # -------------------------------------------------------------------------
    # --- Signals
    def pre_save(self, **kwargs):
        """Docstring."""
        pass

    def post_save(self, created, **kwargs):
        """Docstring."""
        pass

    def pre_delete(self, **kwargs):
        """Docstring."""
        pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass
