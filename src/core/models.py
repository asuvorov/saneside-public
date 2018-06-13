import inspect

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

import pendulum

from annoying.functions import get_object_or_None
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django_countries.fields import CountryField
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from termcolor import colored

from api.sendgrid_api import send_templated_email
from core.choices import (
    SOCIAL_APP, social_app_choices,
    social_app_icons,
    social_app_buttons,
    )
from core.decorators import autoconnect
from core.utils import (
    get_purified_str,
    get_unique_filename,
    )


# -----------------------------------------------------------------------------
# --- TEMPORARY FILE
# -----------------------------------------------------------------------------
def tmp_directory_path(instance, filename):
    """Temporary File Directory Path."""
    # --- File Will be uploaded to
    #     MEDIA_ROOT/tmp/<YYYY>/<MM>/<DD>/<filename>
    today = pendulum.today()

    return "tmp/{today}/{fname}".format(
        today=today.format("YYYY/MM/DD", formatter="alternative"),
        fname=filename)


@autoconnect
class TemporaryFile(TimeStampedModel):
    """Temporary File Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    file = models.FileField(
        upload_to=tmp_directory_path)
    name = models.CharField(
        max_length=255)

    # TODO Write cron job for deleting old, not used temporary files,
    # e.g. when submitting form was canceled.

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.file.name)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    class Meta:
        verbose_name = _("temporary file")
        verbose_name_plural = _("temporary files")
        ordering = ["-id", ]

    def pre_save(self, **kwargs):
        """Docstring."""
        pass

    def post_save(self, created, **kwargs):
        """Docstring."""
        pass

    def pre_delete(self, **kwargs):
        """Docstring."""
        try:
            self.file.delete()
        except:
            pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass


# -----------------------------------------------------------------------------
# --- ATTACHMENTS
# -----------------------------------------------------------------------------
def attachment_image_directory_path(instance, filename):
    """Attachment Image Directory Path."""
    # --- File Will be uploaded to
    #     MEDIA_ROOT/<ct_name>/<ct_object_id>/attachments/images/<filename>
    return "{ct}s/{id}/attachments/images/{fname}".format(
        ct=instance.content_type.name,
        id=instance.object_id,
        fname=get_unique_filename(
            filename.split("/")[-1]
            ))


def attachment_document_directory_path(instance, filename):
    """Attachment Document Directory Path."""
    # --- File Will be uploaded to
    #     MEDIA_ROOT/<ct_name>/<ct_object_id>/attachments/documents/<filename>
    return "{ct}s/{id}/attachments/documents/{fname}".format(
        ct=instance.content_type.name,
        id=instance.object_id,
        fname=get_unique_filename(
            filename.split("/")[-1]
            ))


@autoconnect
class AttachedImage(TimeStampedModel):
    """Attached Image Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    name = models.CharField(
        db_index=True,
        max_length=255, null=True, blank=True,
        verbose_name=_("Name"),
        help_text=_("File Name"))
    image = models.ImageField(
        upload_to=attachment_image_directory_path)

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.content_object)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    class Meta:
        verbose_name = _("attached image")
        verbose_name_plural = _("attached images")
        ordering = ["-id", ]

    def pre_save(self, **kwargs):
        """Docstring."""
        pass

    def post_save(self, created, **kwargs):
        """Docstring."""
        pass

    def pre_delete(self, **kwargs):
        """Docstring."""
        try:
            self.image.delete()
        except:
            pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass


@autoconnect
class AttachedDocument(TimeStampedModel):
    """Attached Document Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    name = models.CharField(
        db_index=True,
        max_length=255, null=True, blank=True,
        verbose_name=_("Name"),
        help_text=_("File Name"))
    document = models.FileField(
        upload_to=attachment_document_directory_path)

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.content_object)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    def url(self):
        """Docstring."""
        return self.document.url

    class Meta:
        verbose_name = _("attached document")
        verbose_name_plural = _("attached documents")
        ordering = ["-id", ]

    def pre_save(self, **kwargs):
        """Docstring."""
        pass

    def post_save(self, created, **kwargs):
        """Docstring."""
        pass

    def pre_delete(self, **kwargs):
        """Docstring."""
        try:
            self.document.delete()
        except:
            pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass


@autoconnect
class AttachedUrl(TimeStampedModel):
    """Attached URL Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    url = models.URLField()
    title = models.CharField(
        db_index=True,
        max_length=255, null=True, blank=True,
        verbose_name=_("Title"),
        help_text=_("URL Title"))

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.content_object)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    class Meta:
        verbose_name = _("attached url")
        verbose_name_plural = _("attached urls")
        ordering = ["-id", ]

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


@autoconnect
class AttachedVideoUrl(TimeStampedModel):
    """Attached Video URL Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    url = models.URLField()

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.content_object)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    def get_youtube_video_id(self):
        """Docstring."""
        return get_youtube_video_id(self.url)

    class Meta:
        verbose_name = _("attached video url")
        verbose_name_plural = _("attached video urls")
        ordering = ["-id", ]

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


@autoconnect
class AttachmentMixin(object):
    """Attachment Mixin Class."""

    # -------------------------------------------------------------------------
    # --- Get List of Attachments
    def get_image_list(self):
        """Docstring."""
        images = AttachedImage.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).order_by("-created")

        return images

    def get_document_list(self):
        """Docstring."""
        documents = AttachedDocument.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).order_by("-created")

        return documents

    def get_url_list(self):
        """Docstring."""
        urls = AttachedUrl.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).order_by("-created")

        return urls

    def get_video_url_list(self):
        """Docstring."""
        video_urls = AttachedVideoUrl.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).order_by("-created")

        return video_urls

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


# -----------------------------------------------------------------------------
# --- ADDRESS
# -----------------------------------------------------------------------------
@autoconnect
class Address(TimeStampedModel):
    """Address Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    address_1 = models.CharField(
        db_index=True,
        max_length=80, null=True, blank=True,
        verbose_name=_("Address Line 1"),
        help_text=_("Address Line 1"))
    address_2 = models.CharField(
        db_index=True,
        max_length=80, null=True, blank=True,
        verbose_name=_("Address Line 2"),
        help_text=_("Address Line 2"))
    city = models.CharField(
        db_index=True,
        max_length=80, null=True, blank=True,
        verbose_name=_("City"),
        help_text=_("City"))
    zip_code = models.CharField(
        db_index=True,
        max_length=80, null=True, blank=True,
        verbose_name=_("Zip/Postal Code"),
        help_text=_("Zip/Postal Code"))
    province = models.CharField(
        db_index=True,
        max_length=80, null=True, blank=True,
        verbose_name=_("State/Province"),
        help_text=_("State/Province"))
    country = CountryField(
        db_index=True,
        verbose_name=_("Country"),
        help_text=_("Country"))

    # -------------------------------------------------------------------------
    # --- Notes
    notes = models.TextField(
        null=True, blank=True,
        verbose_name=_("Notes"),
        help_text=_("Here you can provide additional Notes, Directions, and any other Advice, regarding the Location."))

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
        ordering = ["-id", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.short_address)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.full_address

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    @property
    def short_address(self):
        """Docstring."""
        address = u""

        if self.city:
            address += self.city

            if self.province or self.country:
                address += ", "

        if self.province:
            address += self.province

            if self.country:
                address += ", "

        if self.country:
            address += "%s" % (self.country)

        return address

    @property
    def full_address(self):
        """Docstring."""
        address = u""

        if self.address_1 and self.address_2:
            address += "%s %s, " % (self.address_1, self.address_2)
        elif self.address_1:
            address += "%s, " % (self.address_1)
        elif self.address_2:
            address += "%s, " % (self.address_2)

        if self.city:
            address += "%s, " % (self.city)

        if self.province and self.zip_code:
            address += "%s %s, " % (self.province, self.zip_code)
        elif self.province:
            address += "%s, " % (self.province)
        elif self.zip_code:
            address += "%s, " % (self.zip_code)

        if self.country:
            address += "%s" % (self.country)

        return address

    def pre_save(self, **kwargs):
        """Docstring."""
        # ---------------------------------------------------------------------
        # --- Remove special Characters, duplicated and trailing Spaces
        self.address_1 = get_purified_str(self.address_1)
        self.address_2 = get_purified_str(self.address_2)
        self.city = get_purified_str(self.city)
        self.province = get_purified_str(self.province)

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
# --- PHONE
# -----------------------------------------------------------------------------
@autoconnect
class Phone(TimeStampedModel):
    """Phone Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    phone_number = PhoneNumberField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Phone Number"),
        help_text=_("Please, use the International Format, e.g. +1-202-555-0114."))
    phone_number_ext = models.CharField(
        max_length=8, null=True, blank=True,
        verbose_name=_("Ext."),
        help_text=_("Ext."))

    mobile_phone_number = PhoneNumberField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Phone Number"),
        help_text=_("Please, use the International Format, e.g. +1-202-555-0114."))
    mobile_phone_number_ext = models.CharField(
        max_length=8, null=True, blank=True,
        verbose_name=_("Ext."),
        help_text=_("Ext."))

    class Meta:
        verbose_name = _("phone number")
        verbose_name_plural = _("phone numbers")
        ordering = ["-id", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s', '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.phone_number,
            self.mobile_phone_number)

    def __unicode__(self):
        """Docstring."""
        if self.phone_number and self.mobile_phone_number:
            return u"%s\n%s" % (
                self.phone_number,
                self.mobile_phone_number,
                )
        elif self.phone_number:
            return u"%s" % self.phone_number
        elif self.mobile_phone_number:
            return u"%s" % self.mobile_phone_number
        else:
            return ""

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

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


# -----------------------------------------------------------------------------
# --- VIEWS
# -----------------------------------------------------------------------------
class ViewManager(models.Manager):
    """Views Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(ViewManager, self).get_queryset()


@autoconnect
class View(TimeStampedModel):
    """View Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    user = models.ForeignKey(
        User,
        db_index=True)

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    objects = ViewManager()

    class Meta:
        verbose_name = _("view")
        verbose_name_plural = _("views")
        ordering = ["-id", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.content_object)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

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


@autoconnect
class ViewMixin(object):
    """View Mixin Class."""

    # -------------------------------------------------------------------------
    # --- Views
    @property
    def get_views_count(self):
        """Docstring."""
        return View.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).order_by("-created").count()

    def increase_views_count(self, request):
        """Docstring."""
        if request.user.is_authenticated():
            viewing, created = View.objects.get_or_create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.id,
            )

            return created

        return False

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


# -----------------------------------------------------------------------------
# --- COMMENTS
# -----------------------------------------------------------------------------
class CommentManager(models.Manager):
    """Comment Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(CommentManager, self).get_queryset()


@autoconnect
class Comment(TimeStampedModel):
    """Comment Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    user = models.ForeignKey(
        User,
        db_index=True)
    text = models.TextField(
        verbose_name="Text",
        help_text=_("Comment Text"))

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    # -------------------------------------------------------------------------
    # --- Flags
    is_deleted = models.BooleanField(
        default=False)

    objects = CommentManager()

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        ordering = ["created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.content_object)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

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


@autoconnect
class CommentMixin(object):
    """Comment Mixin Class."""

    # -------------------------------------------------------------------------
    # --- Comments
    @property
    def get_comments_count(self):
        """Docstring."""
        return Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            is_deleted=False,
        ).order_by("-created").count()

    def get_comment_list(self):
        """Docsrting."""
        comments = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            is_deleted=False,
        ).order_by("-created")

        return comments

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


# -----------------------------------------------------------------------------
# --- COMPLAINT
# -----------------------------------------------------------------------------
class ComplaintManager(models.Manager):
    """Complaint Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(ComplaintManager, self).get_queryset()


@autoconnect
class Complaint(TimeStampedModel):
    """Complaint Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    user = models.ForeignKey(
        User,
        db_index=True)
    text = models.TextField(
        verbose_name="Text",
        help_text=_("Complaint Text"))

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    # -------------------------------------------------------------------------
    # --- Flags
    is_processed = models.BooleanField(
        default=False)
    is_deleted = models.BooleanField(
        default=False)

    objects = ComplaintManager()

    class Meta:
        verbose_name = _("complaint")
        verbose_name_plural = _("complaints")
        ordering = ["created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.content_object)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

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

    # -------------------------------------------------------------------------
    # --- Methods
    def email_notify_admins_complaint_created(self, request):
        """Send Notification to the Platform Admins."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        for admin_name, admin_email in settings.ADMINS:
            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "Dear, %(user)s.") % {
                    "user":     admin_name,
                }
            htmlbody = _(
                "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" has reported Complaint to %(subject)s \"<a href=\"%(url)s\">%(name)s</a>\" with the following:</p>"
                "<p>%(text)s</p>"
                "<p>Please, don\'t forget to take some Action.</p>") % {
                    "user":     admin_name,
                    "member":   self.user.get_full_name(),
                    "profile":  self.user.profile.public_url(request),
                    "subject":  self.content_type.name.capitalize(),
                    "url":      self.content_object.public_url(request),
                    "name":     self.content_object.name,
                    "text":     self.text,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "common/emails/complaint_created_adm_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "common/emails/complaint_created_adm.txt",
                    "context":  {
                        "user":     self.user.get_full_name(),
                        "profile":  self.user.profile.public_url(request),
                        "subject":  self.content_type.name.capitalize(),
                        "url":      self.content_object.public_url(request),
                        "name":     self.content_object.name,
                        "text":     self.text,
                    },
                },
                template_html={
                    "name":     "emails/base.html",
                    "context":  {
                        "greetings":    greetings,
                        "htmlbody":     htmlbody,
                    },
                },
                from_email=settings.EMAIL_SENDER,
                to=[
                    admin_email,
                ],
                headers=None,
            )


@autoconnect
class ComplaintMixin(object):
    """Complaint Mixin Class."""

    # -------------------------------------------------------------------------
    # --- Ratings and Reviews
    def is_complained_by_user(self, user):
        """Docsrting."""
        is_complained = get_object_or_None(
            Complaint,
            user=user,
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            is_processed=False,
            is_deleted=False,
        )

        if is_complained:
            return True

        return False

    # -------------------------------------------------------------------------
    # --- Complaints
    @property
    def get_complaints_count(self):
        """Docstring."""
        return Complaint.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            is_deleted=False,
        ).order_by("-created").count()

    def get_complaint_list(self):
        """Docsrting."""
        complaints = Complaint.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            is_deleted=False,
        ).order_by("-created")

        return complaints

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


# -----------------------------------------------------------------------------
# --- RATINGS
# -----------------------------------------------------------------------------
class RatingManager(models.Manager):
    """Rating Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(RatingManager, self).get_queryset()


@autoconnect
class Rating(TimeStampedModel):
    """Rating Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True)
    rating = models.PositiveIntegerField(
        db_index=True,
        default=0)

    # -------------------------------------------------------------------------
    # --- Significant Texts
    review_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Review Text"),
        help_text=_("Review Text"))

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    objects = RatingManager()

    class Meta:
        verbose_name = _("rating")
        verbose_name_plural = _("ratings")
        ordering = ["-id", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.content_object,
            self.rating)

    def __unicode__(self):
        """Docstring."""
        return u"%s: %s" % (
            self.content_object,
            self.rating)

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

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


@autoconnect
class RatingMixin(object):
    """Rating Mixin Class."""

    # -------------------------------------------------------------------------
    # --- Ratings and Reviews
    def is_rated_by_user(self, user):
        """Docsrting."""
        is_rated = get_object_or_None(
            Rating,
            author=user,
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        )

        if is_rated:
            return True

        return False

    @property
    def get_rating_count(self):
        """Docsrting."""
        rating_count = Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).count()

        return rating_count

    @property
    def get_rating_avg(self):
        """Docsrting."""
        rating_sum = Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).aggregate(Sum("rating"))

        try:
            if rating_sum["rating__sum"]:
                rating_avg = rating_sum["rating__sum"] / self.get_rating_count

                return rating_avg

        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

            return 0

        return 0

    @property
    def get_rating_avg_float(self):
        """Docsrting."""
        rating_sum = Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).aggregate(Sum("rating"))

        try:
            if rating_sum["rating__sum"]:
                rating_avg = round(
                    rating_sum["rating__sum"] / float(self.get_rating_count),
                    2)

                return rating_avg

        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

            return 0.0

        return 0.0

    def get_rating_percent_for(self, rating):
        """Docsrting."""
        rating_count = Rating.objects.filter(
            rating=rating,
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).count()

        try:
            rating_avg = int(
                (rating_count / float(self.get_rating_count)) * 100)

            return rating_avg

        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

            return 0

        return 0

    @property
    def get_rating_5_percent(self):
        """Docsrting."""
        return self.get_rating_percent_for(5)

    @property
    def get_rating_4_percent(self):
        """Docsrting."""
        return self.get_rating_percent_for(4)

    @property
    def get_rating_3_percent(self):
        """Docsrting."""
        return self.get_rating_percent_for(3)

    @property
    def get_rating_2_percent(self):
        """Docsrting."""
        return self.get_rating_percent_for(2)

    @property
    def get_rating_1_percent(self):
        """Docsrting."""
        return self.get_rating_percent_for(1)

    def get_review_list(self):
        """Docsrting."""
        reviews = Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        ).order_by("-created")

        return reviews

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


# -----------------------------------------------------------------------------
# --- Newsletter
# -----------------------------------------------------------------------------
class NewsletterManager(models.Manager):
    """Newsletter Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(NewsletterManager, self).get_queryset()


@autoconnect
class Newsletter(TimeStampedModel):
    """Newsletter Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="sent_newsletters",
        verbose_name=_("Author"),
        help_text=_("Newsletter Author"))

    title = models.CharField(
        db_index=True,
        max_length=80,
        verbose_name=_("Title"),
        help_text=_("Newsletter Title"))
    content = RichTextUploadingField(
        config_name="awesome_ckeditor",
        null=True, blank=True,
        verbose_name=_("Content"),
        help_text=_("Newsletter Content"))

    # -------------------------------------------------------------------------
    # --- Recipients
    recipients = models.ManyToManyField(
        User,
        blank=True,
        related_name="newsletter_recipients")

    # -------------------------------------------------------------------------
    # --- Flags

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    objects = NewsletterManager()

    class Meta:
        verbose_name = _("newsletter")
        verbose_name_plural = _("newsletters")
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


# -----------------------------------------------------------------------------
# --- SOCIAL LINKS
# -----------------------------------------------------------------------------
class SocialLinkManager(models.Manager):
    """Social Link Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(SocialLinkManager, self).get_queryset()


@autoconnect
class SocialLink(TimeStampedModel):
    """Social Link Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    social_app = models.CharField(
        max_length=16,
        choices=social_app_choices,
        default=SOCIAL_APP.NONE,
        verbose_name=_("Social App"),
        help_text=_("Social App"))
    url = models.URLField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("url"),
        help_text=_("Social Link"))

    # -------------------------------------------------------------------------
    # --- Content Type
    content_type = models.ForeignKey(
        ContentType,
        related_name="content_type_social_links",
        null=True, blank=True, default=None)
    object_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    content_object = fields.GenericForeignKey(
        "content_type", "object_id")

    # -------------------------------------------------------------------------
    # --- Status

    # -------------------------------------------------------------------------
    # --- Significant Texts

    # -------------------------------------------------------------------------
    # --- Significant Dates

    objects = SocialLinkManager()

    class Meta:
        verbose_name = _("social link")
        verbose_name_plural = _("social links")
        ordering = ["created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.social_app)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Properties
    @property
    def stat_social_app_icon(self):
        """Docstring."""
        for code, icon in social_app_icons:
            if self.social_app == code:
                return icon

        return ""

    @property
    def stat_social_app_button(self):
        """Docstring."""
        for code, button in social_app_buttons:
            if self.social_app == code:
                return button

        return ""

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
