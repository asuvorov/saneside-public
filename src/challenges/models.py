import datetime
import inspect

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import ping_google
from django.core.files import File
from django.core.files.storage import default_storage as storage
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django_extensions.db.models import TimeStampedModel
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from phonenumber_field.modelfields import PhoneNumberField
from select_multiple_field.models import SelectMultipleField
from taggit.managers import TaggableManager
from termcolor import colored
from timezone_field import TimeZoneField

from api.sendgrid_api import send_templated_email
from app.utils import update_seo_model_instance_metadata
from challenges.choices import (
    CHALLENGE_STATUS, challenge_status_choices,
    CHALLENGE_MODE, application_choices,
    challenge_category_choices,
    challenge_category_colors,
    challenge_category_icons,
    challenge_category_images,
    PARTICIPATION_STATUS, participation_status_choices,
    RECURRENCE, recurrence_choices,
    MONTH, month_choices,
    DAY_OF_WEEK, day_of_week_choices,
    day_of_month_choices,
    )
from core.decorators import autoconnect
from core.models import (
    Address,
    AttachmentMixin,
    CommentMixin,
    ComplaintMixin,
    RatingMixin,
    ViewMixin,
    )
from invites.models import Invite
from organizations.models import Organization
from core.utils import get_unique_filename


# -----------------------------------------------------------------------------
# --- CHALLENGE CATEGORY STYLE
# -----------------------------------------------------------------------------
def challenge_category_directory_path(instance, filename):
    """Challenge Category Directory Path."""
    # --- File will be uploaded to
    #     MEDIA_ROOT/challenges/categories/<id>/avatars/<filename>
    return "challenges/categories/{id}/avatars/{fname}".format(
        id=instance.id,
        fname=get_unique_filename(
            filename.split("/")[-1]
            ))


class CategoryManager(models.Manager):
    """Category Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(CategoryManager, self).get_queryset()


@autoconnect
class Category(TimeStampedModel):
    """Challenge Category Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    avatar = models.ImageField(
        upload_to=challenge_category_directory_path, blank=True)
    avatar_thumbnail = ImageSpecField(
        source="avatar",
        processors=[
            ResizeToFill(1600, 400)
        ],
        format="JPEG",
        options={
            "quality":  80
        })

    name = models.CharField(
        db_index=True,
        max_length=80,
        verbose_name=_("Name"),
        help_text=_("Category Name"))
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("Description"),
        help_text=_("Category Description"))
    slug = AutoSlugField(
        populate_from="name", unique=True, always_update=False)

    category = models.CharField(
        max_length=4, null=True, blank=True,
        choices=challenge_category_choices,
        verbose_name=_("Category"),
        help_text=_("Category"))
    color = models.CharField(
        max_length=4, null=True, blank=True,
        choices=challenge_category_colors,
        verbose_name=_("Color"),
        help_text=_("Category Color"))
    icon = models.CharField(
        max_length=4, null=True, blank=True,
        choices=challenge_category_icons,
        verbose_name=_("Icon"),
        help_text=_("Category Icon"))
    image = models.CharField(
        max_length=4, null=True, blank=True,
        choices=challenge_category_images,
        verbose_name=_("Image"),
        help_text=_("Category Image"))

    objects = CategoryManager()

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["id", ]

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

    image_tag.short_description = "Image"
    image_tag.allow_tags = True

    # -------------------------------------------------------------------------
    # --- Signals
    def pre_save(self, **kwargs):
        """Docstring."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    def post_save(self, created, **kwargs):
        """Docstring."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    def pre_delete(self, **kwargs):
        """Docstring."""
        pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass


# -----------------------------------------------------------------------------
# --- CHALLENGE
# -----------------------------------------------------------------------------
def challenge_directory_path(instance, filename):
    """Challenge Directory Path."""
    # --- File will be uploaded to
    #     MEDIA_ROOT/challenges/<id>/avatars/<filename>
    return "challenges/{id}/avatars/{fname}".format(
        id=instance.id,
        fname=get_unique_filename(
            filename.split("/")[-1]
            ))


class ChallengeManager(models.Manager):
    """Challenge Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(ChallengeManager, self).get_queryset()

    def get_upcoming(self):
        """Docstring."""
        return self.get_queryset().filter(
            status=CHALLENGE_STATUS.UPCOMING,
            start_date__gte=datetime.date.today(),
        )

    def get_dateless_upcoming(self):
        """Docstring."""
        return self.get_queryset().filter(
            Q(start_date__gte=datetime.date.today()) |
            Q(recurrence=RECURRENCE.DATELESS),
            status=CHALLENGE_STATUS.UPCOMING
        )


@autoconnect
class Challenge(
        AttachmentMixin, CommentMixin, ComplaintMixin, RatingMixin, ViewMixin,
        TimeStampedModel):
    """Challenge Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="posted_challenges",
        verbose_name=_("Author"),
        help_text=_("Challenge Author"))
    avatar = models.ImageField(
        upload_to=challenge_directory_path)

    name = models.CharField(
        db_index=True,
        max_length=80,
        verbose_name=_("Name"),
        help_text=_("Challenge Name"))
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("Description"),
        help_text=_("Challenge Description"))
    slug = AutoSlugField(
        populate_from="name", unique=True, always_update=False)

    # -------------------------------------------------------------------------
    # --- Tags & Category
    tags = TaggableManager(
        through=None, blank=True,
        verbose_name=_("Tags"),
        help_text=_("A comma-separated List of Tags."))
    hashtag = models.CharField(
        db_index=True,
        max_length=80, null=True, blank=True,
        verbose_name=_("Hashtag"),
        help_text=_("Hashtag"))
    category = models.CharField(
        max_length=4, null=True, blank=True,
        choices=challenge_category_choices,
        verbose_name=_("Category"),
        help_text=_("Challenge Category"))

    status = models.CharField(
        max_length=2,
        choices=challenge_status_choices, default=CHALLENGE_STATUS.UPCOMING,
        verbose_name=_("Status"),
        help_text=_("Challenge Status"))
    application = models.CharField(
        max_length=2,
        choices=application_choices, default=CHALLENGE_MODE.FREE_FOR_ALL,
        verbose_name=_("Application"),
        help_text=_("Challenge Application"))

    # -------------------------------------------------------------------------
    # --- Location
    addressless = models.BooleanField(
        default=False,
        verbose_name=_("I will provide the Location later, if any."),
        help_text=_("I will provide the Location later, if any."))
    address = models.ForeignKey(
        Address,
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Address"),
        help_text=_("Challenge Location"))

    # -------------------------------------------------------------------------
    # --- Duration
    duration = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Duration (hours)"),
        help_text=_("Challenge Duration"))

    # -------------------------------------------------------------------------
    # --- Recurrence
    recurrence = models.CharField(
        max_length=10,
        choices=recurrence_choices, default=RECURRENCE.ONCE,
        verbose_name=_("Recurrence"),
        help_text=_("Challenge Recurrence"))
    month = SelectMultipleField(
        max_length=64,
        choices=month_choices, default=MONTH.NONE,
        verbose_name=_("Month"),
        help_text=_("Month"))
    day_of_week = SelectMultipleField(
        max_length=64,
        choices=day_of_week_choices, default=DAY_OF_WEEK.NONE,
        verbose_name=_("Day of Week"),
        help_text=_("Day of Week"))
    day_of_month = SelectMultipleField(
        max_length=64,
        choices=day_of_month_choices, default="0",
        verbose_name=_("Day of Month"),
        help_text=_("Day of Month"))

    # -------------------------------------------------------------------------
    # --- Date/Time
    start_date = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Start Date"),
        help_text=_("Challenge Start Date"))
    start_time = models.TimeField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Start Time"),
        help_text=_("Challenge Start Time"))
    start_tz = TimeZoneField(
        default=settings.TIME_ZONE,
        verbose_name=_("Timezone"),
        help_text=_("Challenge Timezone"))

    start_date_time_tz = models.DateTimeField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Start Date/Time with TZ"),
        help_text=_("Challenge Start Date/Time with TZ"))

    # -------------------------------------------------------------------------
    # --- Contact Person. Author by default.
    is_alt_person = models.BooleanField(
        default=False)
    alt_person_fullname = models.CharField(
        max_length=80, null=True, blank=True,
        verbose_name=_("Full Name"),
        help_text=_("Challenge Contact Person full Name"))
    alt_person_email = models.EmailField(
        max_length=80, null=True, blank=True,
        verbose_name=_("Email"),
        help_text=_("Challenge Contact Person Email"))
    alt_person_phone = PhoneNumberField(
        null=True, blank=True,
        verbose_name=_("Phone Number"),
        help_text=_("Please, use the International Format, e.g. +1-202-555-0114."))

    # -------------------------------------------------------------------------
    # --- Related Organization
    organization = models.ForeignKey(
        Organization,
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Organization"),
        help_text=_("Challenge Organization"))

    # -------------------------------------------------------------------------
    # --- Achievements
    achievements = RichTextUploadingField(
        config_name="awesome_ckeditor",
        null=True, blank=True,
        verbose_name=_("Achievements"),
        help_text=_("Achievements"))

    # -------------------------------------------------------------------------
    # --- Closed
    closed_reason = models.TextField(
        null=True, blank=True,
        verbose_name=_("Reason for closing"),
        help_text=_("Reason for closing"))

    # -------------------------------------------------------------------------
    # --- Flags
    is_newly_created = models.BooleanField(
        default=True)

    allow_reenter = models.BooleanField(
        default=False,
        verbose_name=_(
            "Allow Members to apply again to the Challenge after withdrawing their Application."),
        help_text=_(
            "Allow Members to apply again to the Challenge after withdrawing their Application."))

    accept_automatically = models.BooleanField(
        default=False,
        verbose_name=_(
            "Automatically accept Participants' Experience Reports after the Challenge completed."),
        help_text=_(
            "Automatically accept Participants' Experience Reports after the Challenge completed."))
    acceptance_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Acceptance Text"),
        help_text=_(
            "This Text will automatically appear as an Acknowledgment Text for each Participant after Challenge has been marked as completed."))

    objects = ChallengeManager()

    class Meta:
        verbose_name = _("challenge")
        verbose_name_plural = _("challenges")
        ordering = ["-created", ]

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
    # --- Helpers
    @property
    def get_start_date(self):
        """Docstring."""
        return unicode(self.start_date)

    @property
    def get_start_time(self):
        """Docstring."""
        return unicode(self.start_time)

    @property
    def stat_category_name(self):
        """Docstring."""
        for code, name in challenge_category_choices:
            if self.category == code:
                return name

        return ""

    @property
    def stat_category_color(self):
        """Docstring."""
        for code, color in challenge_category_colors:
            if self.category == code:
                return color

        return ""

    @property
    def stat_category_icon(self):
        """Docstring."""
        for code, icon in challenge_category_icons:
            if self.category == code:
                return icon

        return ""

    @property
    def stat_application_name(self):
        """Docstring."""
        for code, name in application_choices:
            if self.application == code:
                return name

        return ""

    @property
    def stat_status_name(self):
        """Docstring."""
        for code, name in challenge_status_choices:
            if self.status == code:
                return name

        return ""

    # -------------------------------------------------------------------------
    # --- Challenge direct URL
    def public_url(self, request=None):
        """Docstring."""
        if request:
            DOMAIN_NAME = request.get_host()
        else:
            DOMAIN_NAME = settings.DOMAIN_NAME

        url = reverse(
            "challenge-details", kwargs={
                "slug":     self.slug,
            })
        challenge_link = u"http://{domain}{url}".format(
            domain=DOMAIN_NAME,
            url=url,
            )

        return challenge_link

    def get_absolute_url(self):
        """Method to be called by Django Sitemap Framework."""
        url = reverse(
            "challenge-details", kwargs={
                "slug":     self.slug,
            })

        return url

    # -------------------------------------------------------------------------
    # --- Challenge Status Flags
    @property
    def is_draft(self):
        """Docstring."""
        return self.status == CHALLENGE_STATUS.DRAFT

    @property
    def is_upcoming(self):
        """Docstring."""
        return self.status == CHALLENGE_STATUS.UPCOMING

    @property
    def is_complete(self):
        """Docstring."""
        return self.status == CHALLENGE_STATUS.COMPLETE

    @property
    def is_expired(self):
        """Docstring."""
        return self.status == CHALLENGE_STATUS.EXPIRED

    @property
    def is_closed(self):
        """Docstring."""
        return self.status == CHALLENGE_STATUS.CLOSED

    # -------------------------------------------------------------------------
    # --- Challenge Mode Flags
    @property
    def is_free_for_all(self):
        """Docstring."""
        return self.application == CHALLENGE_MODE.FREE_FOR_ALL

    @property
    def is_confirmation_required(self):
        """Docstring."""
        return self.application == CHALLENGE_MODE.CONFIRMATION_REQUIRED

    # -------------------------------------------------------------------------
    # --- Challenge Recurrence Flags
    @property
    def is_dateless(self):
        """Docstring."""
        return self.recurrence == RECURRENCE.DATELESS

    # -------------------------------------------------------------------------
    # --- Challenge custom Flags
    @property
    def is_overdue(self):
        """Docstring."""
        if self.is_dateless:
            return False

        if self.start_date:
            return self.start_date < datetime.date.today()

        return False

    @property
    def is_happened(self):
        """Docstring."""
        return self.is_complete or self.is_overdue

    @property
    def has_waiting_for_confirmation(self):
        """Docstring."""
        if Participation.objects.filter(
                status=PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
                challenge=self):
            return True

        return False

    @property
    def has_waiting_for_acknowledgement(self):
        """Docstring."""
        if Participation.objects.filter(
                status=PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT,
                challenge=self):
            return True

        return False

    # -------------------------------------------------------------------------
    # --- Challenge Query Sets
    def get_acknowledged_qs(self):
        """Return participations with Acknowledged status."""
        return Participation.objects.filter(
            challenge=self,
            status=PARTICIPATION_STATUS.ACKNOWLEDGED)

    # -------------------------------------------------------------------------
    # --- Challenge Counters
    @property
    def get_waiting_for_confirmation_count(self):
        """Docstring."""
        return Participation.objects.filter(
            challenge=self,
            status=PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION).count()

    @property
    def get_confirmed_count(self):
        """Docstring."""
        return Participation.objects.filter(
            challenge=self,
            status=PARTICIPATION_STATUS.CONFIRMED).count()

    @property
    def get_waiting_for_acknowledgement_count(self):
        """Docstring."""
        return Participation.objects.filter(
            challenge=self,
            status=PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT).count()

    def get_start_date_time_tz(self, **kwargs):
        """Docstring."""
        if self.start_date and self.start_time:
            return self.start_tz.localize(
                datetime.datetime.combine(
                    self.start_date,
                    self.start_time
                    ))

        return None

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

    def challenge_url(self):
        """Docstring."""
        try:
            return u"<a href=\"{url}\" target=\"_blank\">{url}</a>".format(
                url=self.public_url())
        except:
            pass

        return ""

    challenge_url.short_description = "Challenge URL"
    challenge_url.allow_tags = True

    def email_notify_admin_chl_drafted(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.author.first_name,
            }
        htmlbody = _(
            "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\" Draft, was successfully created.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_draft_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_draft.txt",
                "context":  {
                    "user":             self.author,
                    "challenge":        self,
                    "challenge_link":   self.public_url(request),
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
                self.author.email,
            ],
            headers=None,
        )

    def email_notify_admin_chl_created(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.author.first_name,
            }
        htmlbody = _(
            "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was successfully created.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_created_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_created.txt",
                "context":  {
                    "user":             self.author,
                    "challenge":        self,
                    "challenge_link":   self.public_url(request),
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
                self.author.email,
            ],
            headers=None,
        )

    def email_notify_alt_person_chl_created(self, request=None):
        """Send Notification to the Challenge alternative Contact Person."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        if not self.is_alt_person:
            return

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.alt_person_fullname,
            }
        htmlbody = _(
            "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was successfully created, and you were added as a contact Person to it.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_created_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_created_alt.txt",
                "context":  {
                    "user":             self.alt_person_fullname,
                    "challenge":        self,
                    "challenge_link":   self.public_url(request),
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
                self.alt_person_email,
            ],
            headers=None,
        )

    def email_notify_org_subscribers_chl_created(self, request=None):
        """Send Notification to the Challenge Organization Subscribers."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        if not self.organization:
            return

        for subscriber in self.organization.subscribers.all():
            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "The \"<a href=\"%(url)s\">%(name)s</a>\" recent Activity.") % {
                    "name":     self.organization.name,
                    "url":      self.organization.public_url(request),
                }
            htmlbody = _(
                "<p>Dear, %(user)s,</p>"
                "<p>The Organization \"<a href=\"%(org_url)s\">%(org_name)s</a>\" has just created new Challenge \"<a href=\"%(chl_url)s\">%(chl_name)s</a>\".</p>"
                "<p>You have received this Email, because you're subscribed to the Organization\'s Newsletters and Activity Notifications.</p>") % {
                    "user":         subscriber.first_name,
                    "org_name":     self.organization,
                    "org_url":      self.organization.public_url(request),
                    "chl_name":     self,
                    "chl_url":      self.public_url(request),
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "organizations/emails/organization_activity_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "organizations/emails/organization_activity.txt",
                    "context":  {
                        "user":                 subscriber,
                        "organization":         self.organization,
                        "organization_link":    self.organization.public_url(request),
                        "challenge":            self,
                        "challenge_link":       self.public_url(request),
                    },
                },
                template_html={
                    "name": "emails/base.html",
                    "context":  {
                        "greetings":    greetings,
                        "htmlbody":     htmlbody,
                    },
                },
                from_email=settings.EMAIL_SENDER,
                to=[
                    subscriber.email,
                ],
                headers=None,
            )

    def email_notify_admin_chl_edited(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.author.first_name,
            }
        htmlbody = _(
            "<p>Your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was modified.</p>") % {
                "url":          self.public_url(request),
                "name":         self.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_modified_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_modified_adm.txt",
                "context":  {
                    "admin":            self.author,
                    "challenge":        self,
                    "challenge_link":   self.public_url(request),
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
                self.author.email,
            ],
            headers=None,
        )

    def email_notify_alt_person_chl_edited(self, request=None):
        """Send Notification to the Challenge alternative Contact Person."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        if not self.is_alt_person:
            return

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.alt_person_fullname,
            }
        htmlbody = _(
            "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\", where you added as a contact Person, was modified.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_modified_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_modified_alt.txt",
                "context":  {
                    "user":             self.alt_person_fullname,
                    "challenge":        self,
                    "challenge_link":   self.public_url(request),
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
                self.alt_person_email,
            ],
            headers=None,
        )

    def email_notify_admin_chl_completed(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # -------------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.author.first_name,
            }
        htmlbody = _(
            "<p>Your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was complete!</p>"
            "<p>Experience Report Requests were sent to all signed up to the Challenge Members.</p>"
            "<p>Please, don\'t forget to accept, or reject the Members\' Experience Reports.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_complete_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_complete.txt",
                "context":  {
                    "admin":            self.author,
                    "challenge":        self,
                    "challenge_link":   self.public_url(request),
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
                self.author.email,
            ],
            headers=None,
        )

    def email_notify_admin_chl_cloned(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # -------------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.author.first_name,
            }
        htmlbody = _(
            "<p>Your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was cloned!</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_cloned_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_cloned_adm.txt",
                "context":  {
                    "admin":            self.author,
                    "challenge":        self,
                    "challenge_link":   self.public_url(request),
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
                self.author.email,
            ],
            headers=None,
        )

    def email_notify_admin_chl_closed(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # -------------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.author.first_name,
            }
        htmlbody = _(
            "<p>Your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was closed!</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_closed_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_closed_adm.txt",
                "context":  {
                    "admin":            self.author,
                    "challenge":        self,
                    "challenge_link":   self.public_url(request),
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
                self.author.email,
            ],
            headers=None,
        )

    # -------------------------------------------------------------------------
    # --- Signals
    def pre_save(self, **kwargs):
        """Docstring."""
        if self.start_date and self.start_time:
            self.start_date_time_tz = self.start_tz.localize(
                datetime.datetime.combine(
                    self.start_date,
                    self.start_time
                    ))

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
            title=self.name,
            description=self.description,
            keywords=", ".join(self.tags.names()),
            heading=self.name,
            path=self.get_absolute_url(),
            object_id=self.id,
            content_type_id=ContentType.objects.get_for_model(self).id,
        )

        # ---------------------------------------------------------------------
        # --- The Path for uploading Avatar Images is:
        #
        #            MEDIA_ROOT/challenges/<id>/avatars/<filename>
        #
        # --- As long as the uploading Path is being generated before
        #     the Challenge Instance gets assigned with the unique ID,
        #     the uploading Path for the brand new Challenge looks like:
        #
        #            MEDIA_ROOT/challenges/None/avatars/<filename>
        #
        # --- To fix this:
        #     1. Open the Avatar File in the Path;
        #     2. Assign the Avatar File Content to the Challenge Avatar Object;
        #     3. Save the Challenge Instance. Now the Avatar Image in the
        #        correct Path;
        #     4. Delete previous Avatar File;
        #
        if created:
            avatar = File(storage.open(self.avatar.file.name, "rb"))

            self.avatar = avatar
            self.save()

            if "challenges/None/avatars/" in avatar.file.name:
                storage.delete(avatar.file.name)

    def pre_delete(self, **kwargs):
        """Docstring."""
        # ---------------------------------------------------------------------
        # --- Remove related Invites, if any.
        print colored("[---   LOG   ---] Going to remove Invites, related with the Instance", "green")

        try:
            content_type = ContentType.objects.get_for_model(self)

            related_invites = Invite.objects.filter(
                content_type=content_type,
                object_id=self.id,
                )

            print colored("[---  DUMP   ---] RELATED INVITES : %s" % related_invites, "yellow")

            related_invites.delete()

        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

    def post_delete(self, **kwargs):
        """Docstring."""
        pass


@autoconnect
class ChallengeMixin(object):
    """Challenge Mixin Class."""

    # -------------------------------------------------------------------------
    # --- Challenges
    def get_admin_challenges(self):
        """Get Challenges, where User is Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        orgs = self.user.created_organizations.all()
        admin_challenges = Challenge.objects.filter(
            Q(organization__in=orgs) |
            Q(author=self.user)
        )

        return admin_challenges

    @property
    def get_admin_challenges_action_required(self):
        """Return List of the Challenges which require Action."""
        admin_challenges = self.get_admin_challenges().order_by("start_date")

        admin_challenges_action_required = admin_challenges.filter(
            Q(
                pk__in=Participation.objects.filter(
                    status__in=[
                        PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
                        PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT,
                    ]
                ).values_list(
                    "challenge_id", flat=True
                )
            ) |
            Q(
                start_date__lt=datetime.date.today(),
                status=CHALLENGE_STATUS.UPCOMING,
            )
        )

        return admin_challenges_action_required

    @property
    def get_admin_challenges_upcoming(self):
        """Return List of upcoming Challenges."""
        admin_challenges = self.get_admin_challenges().order_by("start_date")

        admin_challenges_upcoming = admin_challenges.filter(
            Q(start_date__gte=datetime.date.today()) |
            Q(recurrence=RECURRENCE.DATELESS),
            status=CHALLENGE_STATUS.UPCOMING
        )

        return admin_challenges_upcoming

    @property
    def get_admin_challenges_completed(self):
        """Return List of completed Challenges."""
        admin_challenges = self.get_admin_challenges().order_by("start_date")

        admin_challenges_completed = admin_challenges.filter(
            status=CHALLENGE_STATUS.COMPLETE,
        )

        return admin_challenges_completed

    @property
    def get_admin_challenges_draft(self):
        """Return List of draft Challenges."""
        admin_challenges = self.get_admin_challenges().order_by("start_date")

        admin_challenges_draft = admin_challenges.filter(
            status=CHALLENGE_STATUS.DRAFT,
        )

        return admin_challenges_draft


# -----------------------------------------------------------------------------
# --- ROLE
# -----------------------------------------------------------------------------
class RoleManager(models.Manager):
    """Role Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(RoleManager, self).get_queryset()


@autoconnect
class Role(TimeStampedModel):
    """Role Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    name = models.CharField(
        db_index=True,
        max_length=80,
        verbose_name=_("Name"),
        help_text=_("Role Name"))
    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity"),
        help_text=_("Quantity"))

    # -------------------------------------------------------------------------
    # --- Related Objects
    challenge = models.ForeignKey(
        Challenge,
        db_index=True,
        null=True, blank=True,
        related_name="challenge_roles",
        verbose_name=_("Challenge"),
        help_text=_("Challenge"))

    # -------------------------------------------------------------------------
    # --- Status

    # -------------------------------------------------------------------------
    # --- Significant Texts

    # -------------------------------------------------------------------------
    # --- Significant Dates

    objects = RoleManager()

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        ordering = ["created", ]

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
# --- PARTICIPATION
# -----------------------------------------------------------------------------
class ParticipationManager(models.Manager):
    """Participation Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(ParticipationManager, self).get_queryset()

    def confirmed(self):
        """Return all confirmed Participations."""
        return self.filter(
            status__in=[
                PARTICIPATION_STATUS.CONFIRMED,
                PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
                PARTICIPATION_STATUS.ACKNOWLEDGED,
                PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT
            ]
        )

    def waiting_for_confirmation(self):
        """Return all waiting for Confirmation Participations."""
        return self.filter(
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION
            ]
        )

    def waiting_for_acknowledgement(self):
        """Return all waiting for Acknowledgment Participations."""
        return self.filter(
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT
            ]
        )


@autoconnect
class Participation(models.Model):
    """Participation Model."""

    # -------------------------------------------------------------------------
    # --- Related Objects
    user = models.ForeignKey(
        User,
        db_index=True,
        related_name="user_participations",
        verbose_name=_("User"),
        help_text=_("Participant"))
    challenge = models.ForeignKey(
        Challenge,
        db_index=True,
        related_name="challenge_participations",
        verbose_name=_("Challenge"),
        help_text=_("Challenge"))
    role = models.ForeignKey(
        Role,
        db_index=True,
        null=True, blank=True,
        related_name="role_participations",
        verbose_name=_("Role"),
        help_text=_("Role, if applicable"))

    # -------------------------------------------------------------------------
    # --- Status
    status = models.CharField(
        max_length=2,
        choices=participation_status_choices,
        default=PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
        verbose_name=_("Status"),
        help_text=_("Participation Status"))

    # -------------------------------------------------------------------------
    # --- Significant Texts
    application_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Application Text"),
        help_text=_("Application Text"))
    cancellation_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Cancellation Text"),
        help_text=_("Cancellation Text"))
    selfreflection_activity_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Experience Report - Activity Text"),
        help_text=_("Experience Report - Activity Text"))
    selfreflection_learning_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Experience Report - learning Text"),
        help_text=_("Experience Report - learning Text"))
    selfreflection_rejection_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Experience Report - Rejection Text"),
        help_text=_("Experience Report - Rejection Text"))
    acknowledgement_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Acknowledgement Text"),
        help_text=_("Acknowledgement Text"))

    # -------------------------------------------------------------------------
    # --- Significant Dates
    date_created = models.DateField(
        db_index=True,
        auto_now_add=True,
        verbose_name=_("Date created"),
        help_text=_("Date created"))
    date_accepted = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Date accepted"),
        help_text=_("Date accepted"))
    date_cancelled = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Date canceled"),
        help_text=_("Date canceled"))
    date_selfreflection = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Date of the Experience Report"),
        help_text=_("Date of receiving of the Experience Report"))
    date_selfreflection_rejection = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Date of the Experience Report Rejection"),
        help_text=_("Date of Rejection of the Experience Report"))
    date_acknowledged = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Date acknowledged"),
        help_text=_("Date of acknowledging of the Experience Report"))

    objects = ParticipationManager()

    class Meta:
        verbose_name = _("participation")
        verbose_name_plural = _("participations")
        ordering = ["-date_created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s' in %s)>" % (
            self.__class__.__name__,
            self.id,
            self.user.username,
            self.challenge.name)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    @property
    def stat_participation_status_name(self):
        """Docstring."""
        for code, name in participation_status_choices:
            if self.status == code:
                return name

        return ""

    # -------------------------------------------------------------------------
    # --- Participation Statuses
    @property
    def is_waiting_for_confirmation(self):
        """Docstring."""
        return self.status == PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION

    @property
    def is_confirmation_denied(self):
        """Docstring."""
        return self.status == PARTICIPATION_STATUS.CONFIRMATION_DENIED

    @property
    def is_confirmed(self):
        """Docstring."""
        return self.status == PARTICIPATION_STATUS.CONFIRMED

    @property
    def is_confirmed_full(self):
        """Docstring."""
        return self.status in [
            PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
            PARTICIPATION_STATUS.CONFIRMED,
            PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
            PARTICIPATION_STATUS.ACKNOWLEDGED,
            PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT,
        ]

    @property
    def is_cancelled_by_admin(self):
        """Docstring."""
        return self.status == PARTICIPATION_STATUS.CANCELLED_BY_ADMIN

    @property
    def is_cancelled_by_user(self):
        """Docstring."""
        return self.status == PARTICIPATION_STATUS.CANCELLED_BY_USER

    @property
    def is_waiting_for_selfreflection(self):
        """Docstring."""
        return self.status == PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION

    @property
    def is_waiting_for_acknowledgement(self):
        """Docstring."""
        return self.status == PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT

    @property
    def is_acknowledged(self):
        """Docstring."""
        return self.status == PARTICIPATION_STATUS.ACKNOWLEDGED

    # -------------------------------------------------------------------------
    # --- Participation Query Sets

    # -------------------------------------------------------------------------
    # --- Participation custom Flags
    @property
    def is_selfreflection_rejected(self):
        """Docstring."""
        if (
                self.status == PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION and
                self.selfreflection_rejection_text and (
                    self.selfreflection_learning_text or
                    self.selfreflection_activity_text)):
            return True

        return False

    # -------------------------------------------------------------------------
    # --- Class Methods
    @classmethod
    def email_notify_participants_datetime_chl_edited(
            cls, request=None, challenge=None):
        """Send Notification to the Challenge Participants."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        upcoming_participations = cls.objects.filter(
            challenge=challenge,
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
                PARTICIPATION_STATUS.CONFIRMED,
            ]
        )

        for participation in upcoming_participations:
            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "Dear, %(user)s.") % {
                    "user":     participation.user.first_name,
                }
            htmlbody = _(
                "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\", you signed up for, was modified.</p>"
                "<p>You are now signed up for the Challenge on %(start_date)s at %(start_time)s.</p>"
                "<p>Please don\'t forget to show up!</p>") % {
                    "url":          challenge.public_url(request),
                    "name":         challenge.name,
                    "start_date":   challenge.get_start_date,
                    "start_time":   challenge.get_start_time,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "challenges/emails/challenge_modified_usr_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "challenges/emails/challenge_modified_usr.txt",
                    "context":  {
                        "user":             participation.user,
                        "challenge":        challenge,
                        "challenge_link":   challenge.public_url(request),
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
                    participation.user.email,
                ],
                headers=None,
            )

    @classmethod
    def email_notify_participants_application_chl_edited(
            cls, request=None, challenge=None):
        """Send Notification to the Challenge Participants."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        waiting_for_confirmation_participations = cls.objects.filter(
            challenge=challenge,
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
            ]
        )

        # ---------------------------------------------------------------------
        # --- If Challenge Admin changed the Challenge Status from
        #     "Confirmation required" to "Free for all", automatically accept
        #     all the People, who are currently waiting for their Applications
        #     to be accepted, and inform them by Email about this.
        for participation in waiting_for_confirmation_participations:
            participation.status = PARTICIPATION_STATUS.CONFIRMED
            participation.date_accepted = datetime.datetime.now()
            participation.save()

            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "Dear, %(user)s.") % {
                    "user":     participation.user.first_name,
                }
            htmlbody = _(
                "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\", you signed up for, was modified.</p>"
                "<p>You are now signed up for the Challenge on %(start_date)s at %(start_time)s.</p>"
                "<p>Please don\'t forget to show up!</p>") % {
                    "url":          challenge.public_url(request),
                    "name":         challenge.name,
                    "start_date":   challenge.get_start_date,
                    "start_time":   challenge.get_start_time,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "challenges/emails/challenge_modified_usr_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "challenges/emails/challenge_modified_usr.txt",
                    "context":  {
                        "user":             participation.user,
                        "challenge":        challenge,
                        "challenge_link":   challenge.public_url(request),
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
                    participation.user.email,
                ],
                headers=None,
            )

    @classmethod
    def email_notify_participants_location_chl_edited(
            cls, request=None, challenge=None):
        """Send Notification to the Challenge Participants."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        upcoming_participations = cls.objects.filter(
            challenge=challenge,
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
                PARTICIPATION_STATUS.CONFIRMED,
            ]
        )

        for participation in upcoming_participations:
            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "Dear, %(user)s.") % {
                    "user":     participation.user.first_name,
                }
            htmlbody = _(
                "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\", you signed up for, was modified.</p>"
                "<p>The new Locations is %(address)s.</p>"
                "<p>Please don\'t forget to show up!</p>") % {
                    "url":          challenge.public_url(request),
                    "address":      challenge.address.full_address,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "challenges/emails/challenge_modified_usr_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "challenges/emails/challenge_modified_usr.txt",
                    "context":  {
                        "user":             participation.user,
                        "challenge":        challenge,
                        "challenge_link":   challenge.public_url(request),
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
                    participation.user.email,
                ],
                headers=None,
            )

    @classmethod
    def email_notify_participants_chl_reporting_materials(
            cls, request=None, challenge=None):
        """Send Notification to the Challenge Participants."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        upcoming_participations = cls.objects.filter(
            challenge=challenge,
            status__in=[
                PARTICIPATION_STATUS.CONFIRMED,
                PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
                PARTICIPATION_STATUS.ACKNOWLEDGED,
                PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT
            ]
        )

        for participation in upcoming_participations:
            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "Dear, %(user)s.") % {
                    "user":     participation.user.first_name,
                }
            htmlbody = _(
                "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\", you participated, has added and/or edited the reporting Materials.</p>") % {
                    "url":          challenge.public_url(request),
                    "name":         challenge.name,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "challenges/emails/challenge_reporting_materials_usr_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "challenges/emails/challenge_reporting_materials_usr.txt",
                    "context":  {
                        "user":             participation.user,
                        "challenge":        challenge,
                        "challenge_link":   challenge.public_url(request),
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
                    participation.user.email,
                ],
                headers=None,
            )

    @classmethod
    def email_notify_participants_chl_completed(
            cls, request=None, challenge=None):
        """Send Notification to the Challenge Participants."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- CONFIRMED -->> WAITING FOR SELFREFLECTION
        # ---------------------------------------------------------------------
        participations = cls.objects.filter(
            challenge=challenge,
            status__in=[
                PARTICIPATION_STATUS.CONFIRMED,
                PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
                PARTICIPATION_STATUS.ACKNOWLEDGED,
                PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT
            ]
        )

        for participation in participations:
            participation.status =\
                PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION
            participation.save()

            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "Dear, %(user)s.") % {
                    "user":     participation.user.first_name,
                }
            htmlbody = _(
                "<p>Thank you for participating in the Challenge \"<a href=\"%(url)s\">%(name)s</a>\"</p>"
                "<p>Please, submit your Experience Report within %(time)s Days.</p>") % {
                    "url":      challenge.public_url(request),
                    "name":     challenge.name,
                    "time":     settings.SELFREFLECTION_SUBMIT_DURATION_PERIOD,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "challenges/emails/challenge_participation_sr_request_usr_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "challenges/emails/challenge_participation_sr_request_usr.txt",
                    "context":  {
                        "user":             participation.user,
                        "challenge":        challenge,
                        "challenge_link":   challenge.public_url(request),
                        "time":             settings.SELFREFLECTION_SUBMIT_DURATION_PERIOD,
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
                    participation.user.email,
                ],
                headers=None,
            )

        # ---------------------------------------------------------------------
        # --- WAITING FOR CONFIRMATION -->> CANCELLED BY ADMIN
        # ---------------------------------------------------------------------
        participations = cls.objects.filter(
            challenge=challenge,
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION
            ]
        )

        for participation in participations:
            participation.status = PARTICIPATION_STATUS.CANCELLED_BY_ADMIN
            participation.cancellation_text = "Challenge completed"
            participation.date_cancelled = datetime.datetime.now()
            participation.save()

            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "Dear, %(user)s.") % {
                    "user":     participation.user.first_name,
                }
            htmlbody = _(
                "<p>Your Application to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was rejected due to the Reason:</p>"
                "<p>Challenge complete.</p>") % {
                    "url":      challenge.public_url(request),
                    "name":     challenge.name,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "challenges/emails/challenge_participation_rejected_usr_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "challenges/emails/challenge_participation_rejected_usr.txt",
                    "context":  {
                        "user":                 participation.user,
                        "challenge":            challenge,
                        "challenge_link":       challenge.public_url(request),
                        "cancellation_text":    "Challenge complete",
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
                    participation.user.email,
                ],
                headers=None,
            )

    @classmethod
    def email_notify_participants_chl_cloned(
            cls, request=None, challenge=None):
        """Send Notification to the Challenge Participants."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        participations = cls.objects.filter(
            challenge=challenge,
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
                PARTICIPATION_STATUS.CONFIRMED
            ]
        )

        for participation in participations:
            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "Dear, %(user)s.") % {
                    "user":     participation.user.first_name,
                }
            htmlbody = _(
                "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\", you signed up for, was cloned for the following Reason:</p>"
                "<p>%(text)s</p>") % {
                    "url":      challenge.public_url(request),
                    "name":     challenge.name,
                    "text":     challenge.closed_reason,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "challenges/emails/challenge_cloned_usr_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "challenges/emails/challenge_cloned_usr.txt",
                    "context":  {
                        "user":             participation.user,
                        "challenge":        challenge,
                        "closed_reason":    challenge.closed_reason,
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
                    participation.user.email,
                ],
                headers=None,
            )

    @classmethod
    def email_notify_participants_chl_closed(
            cls, request=None, challenge=None):
        """Send Notification to the Challenge Participants."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        participations = cls.objects.filter(
            challenge=challenge,
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
                PARTICIPATION_STATUS.CONFIRMED
            ]
        )

        for participation in participations:
            participation.status = PARTICIPATION_STATUS.CANCELLED_BY_ADMIN
            participation.cancellation_text =\
                "Challenge was canceled by Admin"
            participation.save()

            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "Dear, %(user)s.") % {
                    "user":     participation.user.first_name,
                }
            htmlbody = _(
                "<p>The Challenge \"<a href=\"%(url)s\">%(name)s</a>\", you signed up for, was closed for the following Reason:</p>"
                "<p>%(text)s</p>") % {
                    "url":      challenge.public_url(request),
                    "name":     challenge.name,
                    "text":     challenge.closed_reason,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "challenges/emails/challenge_closed_usr_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "challenges/emails/challenge_closed_usr.txt",
                    "context":  {
                        "user":             participation.user,
                        "challenge":        challenge,
                        "closed_reason":    challenge.closed_reason,
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
                    participation.user.email,
                ],
                headers=None,
            )

    # -------------------------------------------------------------------------
    # --- Methods
    def image_tag(self):
        """Render Avatar Thumbnail."""
        if self.user.profile.avatar:
            return u"<img src='{url}' width='{width}' height='{height}' />".format(
                url=self.user.profile.avatar.url,
                width=100,
                height=60,
                )
        else:
            return "(Sin Imagen)"

    image_tag.short_description = "Avatar"
    image_tag.allow_tags = True

    def email_notify_chl_participant_confirmed(self, request=None):
        """Send Notification to the Challenge Participant."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.user.first_name,
            }

        if self.role:
            htmlbody = _(
                "<p>Your Application to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\", for the Role of \"%(role)s\" was accepted!</p>"
                "<p>You are now signed up for the Challenge on %(start_date)s at %(start_time)s.</p>"
                "<p>Please don\'t forget to show up!</p>") % {
                    "url":          self.challenge.public_url(request),
                    "name":         self.challenge.name,
                    "role":         self.role.name,
                    "start_date":   self.challenge.get_start_date,
                    "start_time":   self.challenge.get_start_time,
                }
        else:
            htmlbody = _(
                "<p>Your Application to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\", was accepted!</p>"
                "<p>You are now signed up for the Challenge on %(start_date)s at %(start_time)s.</p>"
                "<p>Please don\'t forget to show up!</p>") % {
                    "url":          self.challenge.public_url(request),
                    "name":         self.challenge.name,
                    "start_date":   self.challenge.get_start_date,
                    "start_time":   self.challenge.get_start_time,
                }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_accepted_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_accepted_usr.txt",
                "context":  {
                    "participation":    self,
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
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
                self.user.email,
            ],
            headers=None,
        )

    def email_notify_chl_admin_participant_confirmed(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.challenge.author.first_name,
            }

        if self.role:
            htmlbody = _(
                "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" was accepted to Participate in your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" for the Role of \"%(role)s\"!</p>") % {
                    "profile":  self.user.profile.public_url(request),
                    "member":   self.user.first_name,
                    "url":      self.challenge.public_url(request),
                    "name":     self.challenge.name,
                    "role":     self.role.name,
                }
        else:
            htmlbody = _(
                "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" was accepted to Participate in your Challenge \"<a href=\"%(url)s\">%(name)s</a>\"!</p>") % {
                    "profile":  self.user.profile.public_url(request),
                    "member":   self.user.first_name,
                    "url":      self.challenge.public_url(request),
                    "name":     self.challenge.name,
                }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_accepted_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_accepted_adm.txt",
                "context":  {
                    "participation":    self,
                    "profile_link":     self.user.profile.public_url(request),
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
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
                self.challenge.author.email,
            ],
            headers=None,
        )

    def email_notify_chl_participant_waiting_conf(self, request=None):
        """Send Notification to the Challenge Participant."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.user.first_name,
            }

        if self.role:
            htmlbody = _(
                "<p>Your Application to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\", for the Role of \"%(role)s\" is waiting for Confirmation!</p>") % {
                    "url":      self.challenge.public_url(request),
                    "name":     self.challenge.name,
                    "role":     self.role.name,
                }
        else:
            htmlbody = _(
                "<p>Your Application to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\", is waiting for Confirmation!</p>") % {
                    "url":      self.challenge.public_url(request),
                    "name":     self.challenge.name,
                }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_pending_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_pending_usr.txt",
                "context":  {
                    "participation":    self,
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
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
                self.user.email,
            ],
            headers=None,
        )

    def email_notify_chl_admin_participant_waiting_conf(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.challenge.author.first_name,
            }

        if self.role:
            htmlbody = _(
                "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" applied to Participate in your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" for the Role of \"%(role)s\" with the following Text:</p>"
                "<p>%(text)s</p>"
                "<p>Please, don\'t forget to accept or reject the Member\'s Application.</p>") % {
                    "profile":  self.user.profile.public_url(request),
                    "member":   self.user.first_name,
                    "url":      self.challenge.public_url(request),
                    "name":     self.challenge.name,
                    "role":     self.role.name,
                    "text":     self.application_text,
                }
        else:
            htmlbody = _(
                "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" applied to Participate in your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" with the following Text:</p>"
                "<p>%(text)s</p>"
                "<p>Please, don\'t forget to accept or reject the Member\'s Application.</p>") % {
                    "profile":  self.user.profile.public_url(request),
                    "member":   self.user.first_name,
                    "url":      self.challenge.public_url(request),
                    "name":     self.challenge.name,
                    "text":     self.application_text,
                }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_pending_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_pending_adm.txt",
                "context":  {
                    "participation":        self,
                    "profile_link":         self.user.profile.public_url(request),
                    "challenge":            self.challenge,
                    "challenge_link":       self.challenge.public_url(request),
                    "application_text":     self.application_text,
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
                self.challenge.author.email,
            ],
            headers=None,
        )

    def email_notify_chl_participant_withdrew(self, request=None):
        """Send Notification to the Challenge Participant."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.user.first_name,
            }
        htmlbody = _(
            "<p>You have withdrawn your Participation in Challenge \"<a href=\"%(url)s\">%(name)s</a>\"!</p>") % {
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_withdrawn_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_withdrawn_usr.txt",
                "context":  {
                    "user":             self.user,
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
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
                self.user.email,
            ],
            headers=None,
        )

    def email_notify_chl_admin_participant_withdrew(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.challenge.author.first_name,
            }
        htmlbody = _(
            "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" withdrew Application for participating in your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" with the following Text:</p>"
            "<p>%(text)s</p>") % {
                "profile":  self.user.profile.public_url(request),
                "member":   self.user.first_name,
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
                "text":     self.cancellation_text,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_withdrawn_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_withdrawn_adm.txt",
                "context":  {
                    "admin":                self.challenge.author,
                    "user":                 self.user,
                    "profile_link":         self.user.profile.public_url(request),
                    "challenge":            self.challenge,
                    "challenge_link":       self.challenge.public_url(request),
                    "cancellation_text":    self.cancellation_text,
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
                self.challenge.author.email,
            ],
            headers=None,
        )

    def email_notify_chl_participant_removed(self, request=None):
        """Send Notification to the Challenge Participant."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.user.first_name,
            }
        htmlbody = _(
            "<p>Your Application to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was removed due to the Reason:</p>"
            "<p>%(text)s</p>") % {
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
                "text":     self.cancellation_text,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_removed_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_removed_usr.txt",
                "context":  {
                    "user":                 self.user,
                    "challenge":            self.challenge,
                    "challenge_link":       self.challenge.public_url(request),
                    "cancellation_text":    self.cancellation_text,
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
                self.user.email,
            ],
            headers=None,
        )

    def email_notify_chl_admin_participant_removed(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.challenge.author.first_name,
            }
        htmlbody = _(
            "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" was removed from participating in your Challenge \"<a href=\"%(url)s\">%(name)s</a>\".</p>") % {
                "profile":  self.user.profile.public_url(request),
                "member":   self.user.first_name,
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_removed_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_removed_adm.txt",
                "context":  {
                    "admin":            self.challenge.author,
                    "user":             self.user,
                    "profile_link":     self.user.profile.public_url(request),
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
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
                self.challenge.author.email,
            ],
            headers=None,
        )

    def email_notify_chl_participant_rejected(self, request=None):
        """Send Notification to the Challenge Participant."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.user.first_name,
            }
        htmlbody = _(
            "<p>Your Application to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was rejected due to the Reason:</p>"
            "<p>%(text)s</p>") % {
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
                "text":     self.cancellation_text,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_rejected_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_rejected_usr.txt",
                "context":  {
                    "user":                 self.user,
                    "challenge":            self.challenge,
                    "challenge_link":       self.challenge.public_url(request),
                    "cancellation_text":    self.cancellation_text,
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
                self.user.email,
            ],
            headers=None,
        )

    def email_notify_chl_admin_participant_rejected(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.challenge.author.first_name,
            }
        htmlbody = _(
            "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" was rejected from participating in your Challenge \"<a href=\"%(url)s\">%(name)s</a>\"!</p>") % {
                "profile":  self.user.profile.public_url(request),
                "member":   self.user.first_name,
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_rejected_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_rejected_adm.txt",
                "context":  {
                    "admin":            self.challenge.author,
                    "user":             self.user,
                    "profile_link":     self.user.profile.public_url(request),
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
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
                self.challenge.author.email,
            ],
            headers=None,
        )

    def email_notify_chl_participant_sr_submitted(self, request=None):
        """Send Notification to the Challenge Participant."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.user.first_name,
            }
        htmlbody = _(
            "<p>Your Experience Report to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\", was submitted.</p>") % {
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_sr_submit_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_sr_submit_usr.txt",
                "context":  {
                    "user":             self.user,
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
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
                self.user.email,
            ],
            headers=None,
        )

    def email_notify_chl_admin_participant_sr_submitted(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.challenge.author.first_name,
            }
        htmlbody = _(
            "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" submitted Experience Report on your Challenge \"<a href=\"%(url)s\">%(name)s</a>\".</p>"
            "<p>Please, accept OR reject Member\'s Experience Report.</p>") % {
                "profile":  self.user.profile.public_url(request),
                "member":   self.user.first_name,
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_sr_submit_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_sr_submit_adm.txt",
                "context":  {
                    "admin":            self.challenge.author,
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
                    "user":             self.user,
                    "profile_link":     self.user.profile.public_url(request),
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
                self.challenge.author.email,
            ],
            headers=None,
        )

    def email_notify_chl_participant_sr_accepted(self, request=None):
        """Send Notification to the Challenge Participant."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.user.first_name,
            }
        htmlbody = _(
            "<p>Your Experience Report to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\", was accepted with following:</p>"
            "<p>%(text)s</p>") % {
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
                "text":     self.challenge.acceptance_text,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_sr_accepted_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_sr_accepted_usr.txt",
                "context":  {
                    "user":                     self.user,
                    "challenge":                self.challenge,
                    "challenge_link":           self.challenge.public_url(request),
                    "acknowledgement_text":     self.acknowledgement_text,
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
                self.user.email,
            ],
            headers=None,
        )

    def email_notify_chl_admin_participant_sr_accepted(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.challenge.author.first_name,
            }
        htmlbody = _(
            "<p>\"<a href=\"%(profile)s\">%(member)s\'s</a>\" Experience Report to your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was accepted!</p>") % {
                "profile":  self.user.profile.public_url(request),
                "member":   self.user.first_name,
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_sr_accepted_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_sr_accepted_adm.txt",
                "context":  {
                    "admin":            self.challenge.author,
                    "user":             self.user,
                    "profile_link":     self.user.profile.public_url(request),
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
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
                self.challenge.author.email,
            ],
            headers=None,
        )

    def email_notify_chl_participant_sr_rejected(self, request=None):
        """Send Notification to the Challenge Participant."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.user.first_name,
            }
        htmlbody = _(
            "<p>Your Experience Report to the Challenge \"<a href=\"%(url)s\">%(name)s</a>\", was rejected due to the Reason:</p>"
            "<p>%(text)s</p>") % {
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
                "text":     self.selfreflection_rejection_text,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_sr_rejected_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_sr_rejected_usr.txt",
                "context":  {
                    "user":                             self.user,
                    "challenge":                        self.challenge,
                    "challenge_link":                   self.challenge.public_url(request),
                    "selfreflection_rejection_text":    self.selfreflection_rejection_text,
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
                self.user.email,
            ],
            headers=None,
        )

    def email_notify_chl_admin_participant_sr_rejected(self, request=None):
        """Send Notification to the Challenge Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # -------------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.challenge.author.first_name,
            }
        htmlbody = _(
            "<p>\"<a href=\"%(profile)s\">%(member)s\'s</a>\" Experience Report to your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" was rejected!</p>") % {
                "profile":  self.user.profile.public_url(request),
                "member":   self.user.first_name,
                "url":      self.challenge.public_url(request),
                "name":     self.challenge.name,
            }

        # -------------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "challenges/emails/challenge_participation_sr_rejected_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "challenges/emails/challenge_participation_sr_rejected_adm.txt",
                "context":  {
                    "admin":            self.challenge.author,
                    "user":             self.user,
                    "profile_link":     self.user.profile.public_url(request),
                    "challenge":        self.challenge,
                    "challenge_link":   self.challenge.public_url(request),
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
                self.challenge.author.email,
            ],
            headers=None,
        )

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


@autoconnect
class ParticipationMixin(object):
    """Participation Mixin Class."""

    # -------------------------------------------------------------------------
    # --- Participations
    @property
    def get_upcoming_participations(self):
        """Return List of upcoming Participations."""
        upcoming_participations = Participation.objects.filter(
            user=self.user,
            challenge__status=CHALLENGE_STATUS.UPCOMING,
            status__in=[
                PARTICIPATION_STATUS.CONFIRMED,
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
            ]
        )

        return upcoming_participations

    @property
    def get_completed_participations(self):
        """Return List of completed Participations."""
        completed_participations = Participation.objects.filter(
            user=self.user,
            challenge__status=CHALLENGE_STATUS.COMPLETE,
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
                PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT,
                PARTICIPATION_STATUS.ACKNOWLEDGED,
            ]
        )

        return completed_participations

    @property
    def get_cancelled_participations(self):
        """Return List of canceled Participations."""
        cancelled_participations = Participation.objects.filter(
            user=self.user,
            challenge__status__in=[
                CHALLENGE_STATUS.UPCOMING,
                CHALLENGE_STATUS.COMPLETE,
            ],
            status__in=[
                PARTICIPATION_STATUS.CANCELLED_BY_USER,
            ]
        )

        return cancelled_participations

    @property
    def get_rejected_participations(self):
        """Return List of rejected Participation."""
        rejected_participations = Participation.objects.filter(
            user=self.user,
            challenge__status__in=[
                CHALLENGE_STATUS.UPCOMING,
                CHALLENGE_STATUS.COMPLETE,
            ],
            status__in=[
                PARTICIPATION_STATUS.CONFIRMATION_DENIED,
                PARTICIPATION_STATUS.CANCELLED_BY_ADMIN,
            ]
        )

        return rejected_participations
