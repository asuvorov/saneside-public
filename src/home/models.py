import inspect

from django.contrib.auth.models import User
from django.contrib.sitemaps import ping_google
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from termcolor import colored

from core.decorators import autoconnect
from core.utils import get_unique_filename


# -----------------------------------------------------------------------------
# --- PARTNER
# -----------------------------------------------------------------------------
def partner_directory_path(instance, filename):
    """Partner Directory Path."""
    # --- File will be uploaded to
    #     MEDIA_ROOT/partners/<id>/avatars/<filename>
    return "partners/{id}/avatars/{fname}".format(
        id=instance.id,
        fname=get_unique_filename(
            filename.split("/")[-1]
            ))


class PartnerManager(models.Manager):
    """Partner Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(PartnerManager, self).get_queryset()


@autoconnect
class Partner(TimeStampedModel):
    """Partner Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    avatar = models.ImageField(
        upload_to=partner_directory_path, blank=True)

    name = models.CharField(
        db_index=True,
        max_length=128, null=True, blank=True,
        default="",
        verbose_name=_("Name"),
        help_text=_("Name"))

    # -------------------------------------------------------------------------
    # --- URLs
    website = models.URLField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Website"),
        help_text=_("Website"))

    objects = PartnerManager()

    class Meta:
        verbose_name = _("partner")
        verbose_name_plural = _("partners")
        ordering = [
            "-id",
        ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.name)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.name

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

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
# --- FAQ SECTION
# -----------------------------------------------------------------------------
class SectionManager(models.Manager):
    """FAQ Section Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(SectionManager, self).get_queryset()


@autoconnect
class Section(TimeStampedModel):
    """FAQ Section Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="authored_faq_sections",
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
# --- FAQ
# -----------------------------------------------------------------------------
class FAQManager(models.Manager):
    """FAQ Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(FAQManager, self).get_queryset()


@autoconnect
class FAQ(TimeStampedModel):
    """FAQ Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True)
    section = models.ForeignKey(
        Section,
        db_index=True,
        related_name="related_faqs",
        verbose_name=_("Section"),
        help_text=_("FAQ Section"))

    question = models.TextField(
        max_length=1024,
        verbose_name=_("Question"),
        help_text=_("Question"))
    answer = RichTextUploadingField(
        config_name="awesome_ckeditor",
        null=True, blank=True,
        verbose_name=_("Answer"),
        help_text=_("Answer"))

    # -------------------------------------------------------------------------
    # --- Flags

    objects = FAQManager()

    class Meta:
        verbose_name = _("frequently asked question")
        verbose_name_plural = _("frequently asked questions")
        ordering = ["-created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.question)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Signals
    def pre_save(self, **kwargs):
        """Docstring."""
        pass

    def post_save(self, created, **kwargs):
        """Docstring."""
        try:
            ping_google()
        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

    def pre_delete(self, **kwargs):
        """Docstring."""
        pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass
