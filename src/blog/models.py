import inspect

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import ping_google
from django.core.files import File
from django.core.files.storage import default_storage as storage
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django_extensions.db.models import TimeStampedModel
from taggit.managers import TaggableManager
from termcolor import colored

from app.utils import update_seo_model_instance_metadata
from blog.choices import (
    POST_STATUS, post_status_choices,
    )
from core.decorators import autoconnect
from core.models import (
    CommentMixin,
    RatingMixin,
    ViewMixin,
    )
from core.utils import get_unique_filename


# -----------------------------------------------------------------------------
# --- POST
# -----------------------------------------------------------------------------
def blog_directory_path(instance, filename):
    """Blog Directory Path."""
    # --- File will be uploaded to
    #     MEDIA_ROOT/blog/<id>/avatars/<filename>
    return "blog/{id}/avatars/{fname}".format(
        id=instance.id,
        fname=get_unique_filename(
            filename.split("/")[-1]
            ))


class PostManager(models.Manager):
    """Post Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(PostManager, self).get_queryset()


@autoconnect
class Post(CommentMixin, RatingMixin, ViewMixin, TimeStampedModel):
    """Post Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="posted_posts",
        verbose_name=_("Post Author"),
        help_text=_("Post Author"))
    avatar = models.ImageField(
        upload_to=blog_directory_path)

    title = models.CharField(
        db_index=True,
        max_length=80,
        verbose_name=_("Title"),
        help_text=_("Post Title"))
    description = RichTextUploadingField(
        config_name="awesome_ckeditor",
        null=True, blank=True,
        verbose_name=_("Short Description"),
        help_text=_("Post short Description"))
    content = RichTextUploadingField(
        config_name="awesome_ckeditor",
        null=True, blank=True,
        verbose_name=_("Content"),
        help_text=_("Post Content"))
    slug = AutoSlugField(
        populate_from="title", unique=True, always_update=False)

    # -------------------------------------------------------------------------
    # --- Tags
    tags = TaggableManager(
        through=None, blank=True,
        verbose_name=_("Tags"),
        help_text=_("A comma-separated List of Tags."))
    hashtag = models.CharField(
        db_index=True,
        max_length=80, null=True, blank=True,
        verbose_name=_("Hashtag"),
        help_text=_("Hashtag"))

    # -------------------------------------------------------------------------
    # --- Flags
    status = models.CharField(
        max_length=2,
        choices=post_status_choices, default=POST_STATUS.DRAFT,
        verbose_name=_("Status"),
        help_text=_("Post Status"))

    objects = PostManager()

    class Meta:
        verbose_name = _("blog post")
        verbose_name_plural = _("blog posts")
        ordering = ["-created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.title)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)

    # -------------------------------------------------------------------------
    # --- Post direct URL
    def public_url(self, request=None):
        """Docstring."""
        if request:
            DOMAIN_NAME = request.get_host()
        else:
            DOMAIN_NAME = settings.DOMAIN_NAME

        url = reverse(
            "post-details", kwargs={
                "slug":     self.slug,
            })
        post_link = u"http://{domain}{url}".format(
            domain=DOMAIN_NAME,
            url=url,
            )

        return post_link

    def get_absolute_url(self):
        """Method to be called by Django Sitemap Framework."""
        url = reverse(
            "post-details", kwargs={
                "slug":     self.slug,
            })

        return url

    # -------------------------------------------------------------------------
    # --- Post Status Flags
    @property
    def is_draft(self):
        """Docstring."""
        return self.status == POST_STATUS.DRAFT

    @property
    def is_visible(self):
        """Docstring."""
        return self.status == POST_STATUS.VISIBLE

    @property
    def is_closed(self):
        """Docstring."""
        return self.status == POST_STATUS.CLOSED

    # -------------------------------------------------------------------------
    # --- Methods
    def image_tag(self):
        """Render Avatar Thumbnail."""
        if self.avatar:
            return u"<img src='{url}' width='{width}' height='{height}' />".format(
                url=self.avatar.url,
                width=100,
                height=60,
                )
        else:
            return "(Sin Imagen)"

    image_tag.short_description = "Avatar"
    image_tag.allow_tags = True

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
            description=self.content,
            keywords=", ".join(self.tags.names()),
            heading=self.title,
            path=self.get_absolute_url(),
            object_id=self.id,
            content_type_id=ContentType.objects.get_for_model(self).id,
        )

        # ---------------------------------------------------------------------
        # --- The Path for uploading Avatar Images is:
        #
        #            MEDIA_ROOT/blog/<id>/avatars/<filename>
        #
        # --- As long as the uploading Path is being generated before
        #     the Blog Instance gets assigned with the unique ID,
        #     the uploading Path for the brand new Blog looks like:
        #
        #            MEDIA_ROOT/blog/None/avatars/<filename>
        #
        # --- To fix this:
        #     1. Open the Avatar File in the Path;
        #     2. Assign the Avatar File Content to the Blog Avatar Object;
        #     3. Save the Blog Instance. Now the Avatar Image in the
        #        correct Path;
        #     4. Delete previous Avatar File;
        #
        if created:
            avatar = File(storage.open(self.avatar.file.name, "rb"))

            self.avatar = avatar
            self.save()

            storage.delete(avatar.file.name)

    def pre_delete(self, **kwargs):
        """Docstring."""
        pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass
