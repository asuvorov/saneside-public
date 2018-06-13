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
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel

from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField
from taggit.managers import TaggableManager
from termcolor import colored

from api.sendgrid_api import send_templated_email
from app.utils import update_seo_model_instance_metadata
from core.decorators import autoconnect
from core.models import (
    Address,
    AttachmentMixin,
    CommentMixin,
    ComplaintMixin,
    Phone,
    RatingMixin,
    ViewMixin,
    )
from core.utils import get_unique_filename
from invites.models import Invite


# -----------------------------------------------------------------------------
# --- ORGANIZATION
# -----------------------------------------------------------------------------
def organization_directory_path(instance, filename):
    """Organization Directory Path."""
    # --- File will be uploaded to
    #     MEDIA_ROOT/organizations/<id>/avatars/<filename>
    return "organizations/{id}/avatars/{fname}".format(
        id=instance.id,
        fname=get_unique_filename(
            filename.split("/")[-1]
            ))


class OrganizationManager(models.Manager):
    """Organization Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(OrganizationManager, self).get_queryset()


@autoconnect
class Organization(
        AttachmentMixin, CommentMixin, ComplaintMixin, RatingMixin, ViewMixin,
        TimeStampedModel):
    """Organization Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="created_organizations",
        verbose_name=_("Author"),
        help_text=_("Organization Author"))
    avatar = models.ImageField(
        upload_to=organization_directory_path)
    name = models.CharField(
        db_index=True,
        max_length=80,
        verbose_name=_("Name"),
        help_text=_("Organization Name"))
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("Description"),
        help_text=_("Organization Description"))
    slug = AutoSlugField(
        populate_from="name", unique=True, always_update=False)

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
    # --- Address & Phone Number
    addressless = models.BooleanField(
        default=False,
        verbose_name=_("I will provide the Location later, if any."),
        help_text=_("I will provide the Location later, if any."))
    address = models.ForeignKey(
        Address,
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Address"),
        help_text=_("Organization Address"))

    phone_number = models.ForeignKey(
        Phone,
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Phone Numbers"),
        help_text=_("Organization Phone Numbers"))

    # -------------------------------------------------------------------------
    # --- URLs
    website = models.URLField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Website"),
        help_text=_("Organization Website"))
    video = models.URLField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Video"),
        help_text=_("Organization Informational Video"))
    email = models.EmailField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Email"),
        help_text=_("Organization Email"))

    # -------------------------------------------------------------------------
    # --- Social Links

    # -------------------------------------------------------------------------
    # --- Subscribers
    subscribers = models.ManyToManyField(
        User,
        db_index=True,
        blank=True,
        related_name="organization_subscribers",
        verbose_name=_("Subscribers"),
        help_text=_("Organization Subscribers"))

    # -------------------------------------------------------------------------
    # --- Contact Person. Author by default.
    is_alt_person = models.BooleanField(
        default=False)
    alt_person_fullname = models.CharField(
        max_length=80, null=True, blank=True,
        verbose_name=_("Full Name"),
        help_text=_("Organization contact Person full Name"))
    alt_person_email = models.EmailField(
        max_length=80, null=True, blank=True,
        verbose_name=_("Email"),
        help_text=_("Organization contact Person Email"))
    alt_person_phone = PhoneNumberField(
        blank=True,
        verbose_name=_("Phone Number"),
        help_text=_("Please, use the International Format, e.g. +1-202-555-0114."))

    # -------------------------------------------------------------------------
    # --- Flags
    is_newly_created = models.BooleanField(
        default=True)
    is_hidden = models.BooleanField(
        default=False)
    is_deleted = models.BooleanField(
        default=False)

    objects = OrganizationManager()

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
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
    # --- Organization direct URL
    def public_url(self, request=None):
        """Docstring."""
        if request:
            DOMAIN_NAME = request.get_host()
        else:
            DOMAIN_NAME = settings.DOMAIN_NAME

        url = reverse(
            "organization-details", kwargs={
                "slug":     self.slug,
            })
        organization_link = u"http://{domain}{url}".format(
            domain=DOMAIN_NAME,
            url=url,
            )

        return organization_link

    def get_absolute_url(self):
        """Method to be called by Django Sitemap Framework."""
        url = reverse(
            "organization-details", kwargs={
                "slug":     self.slug,
            })

        return url

    def get_hours_received(self):
        """Docstring."""
        from challenges.choices import CHALLENGE_STATUS
        from challenges.models import Challenge

        hours_worked = Challenge.objects.filter(
            status=CHALLENGE_STATUS.COMPLETE,
            organization=self,
            ).aggregate(Sum("duration"))

        return hours_worked["duration__sum"]

    def get_upcoming_challenges(self):
        """Docstring."""
        from challenges.choices import CHALLENGE_STATUS
        from challenges.models import Challenge

        upcoming_challenges = Challenge.objects.filter(
            organization=self,
            status=CHALLENGE_STATUS.UPCOMING,
            start_date__gte=datetime.date.today(),
        )

        return upcoming_challenges

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

    def email_notify_admin_org_created(self, request=None):
        """Send Notification to the Organization Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.author.first_name,
            }
        htmlbody = _(
            "<p>The Organization \"<a href=\"%(url)s\">%(name)s</a>\" was successfully created.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "organizations/emails/organization_created_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "organizations/emails/organization_created.txt",
                "context":  {
                    "user":                 self.author,
                    "organization":         self,
                    "organization_link":    self.public_url(request),
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

    def email_notify_alt_person_org_created(self, request=None):
        """Send Notification to the Organization alternative Contact Person."""
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
            "<p>The Organization \"<a href=\"%(url)s\">%(name)s</a>\" was successfully created, and you were added as a Contact Person to it.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "organizations/emails/organization_created_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "organizations/emails/organization_created_alt.txt",
                "context":  {
                    "user":                 self.alt_person_fullname,
                    "organization":         self,
                    "organization_link":    self.public_url(request),
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

    def email_notify_admin_org_modified(self, request=None):
        """Send Notification to the Organization Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.author.first_name,
            }
        htmlbody = _(
            "<p>Your Organization \"<a href=\"%(url)s\">%(name)s</a>\" was modified.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "organizations/emails/organization_modified_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "organizations/emails/organization_modified.txt",
                "context":  {
                    "admin":                self.author,
                    "organization":         self,
                    "organization_link":    self.public_url(request),
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

    def email_notify_alt_person_org_modified(self, request=None):
        """Send Notification to the Organization alternative Contact Person."""
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
            "<p>The Organization \"<a href=\"%(url)s\">%(name)s</a>\", were you added as a Contact Person, was modified!.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "organizations/emails/organization_modified_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "organizations/emails/organization_modified_alt.txt",
                "context":  {
                    "user":                 self.alt_person_fullname,
                    "organization":         self,
                    "organization_link":    self.public_url(request),
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

    def email_notify_admin_org_newsletter_created(
            self, request=None, newsletter=None):
        """Send Notification to the Organization Admin."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        if not newsletter:
            return

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.author.first_name,
            }
        htmlbody = _(
            "<p>The Organization\'s \"<a href=\"%(url)s\">%(name)s</a>\" Newsletter with the Title \"%(title)s\", was successfully created and populated.</p>") % {
                "url":      self.public_url(request),
                "name":     self.name,
                "title":    newsletter.title,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "organizations/emails/organization_newsletter_admin_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "organizations/emails/organization_newsletter_admin.txt",
                "context":  {
                    "admin":                self.author,
                    "organization":         self,
                    "organization_link":    self.public_url(request),
                    "newsletter":           newsletter,
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

    def email_notify_newsletter_populate(
            self, request=None, newsletter=None):
        """Populate Newsletter among Organization's Subscribers."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        for subscriber in self.subscribers.all():
            newsletter.recipients.add(subscriber)

            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            greetings = _(
                "The \"<a href=\"%(url)s\">%(name)s</a>\" Newsletter:<br/>\"%(title)s\"") % {
                    "name":     self.name,
                    "url":      self.public_url(request),
                    "title":    newsletter.title,
                }
            htmlbody = _(
                "<p>%(content)s<br/>You have received this Email, because you're subscribed to the Organization's Newsletters and Activity Notifications.</p>") % {
                    "content":  newsletter.content,
                }

            # -----------------------------------------------------------------
            # --- Send Email
            send_templated_email(
                template_subj={
                    "name":     "organizations/emails/organization_newsletter_subject.txt",
                    "context":  {},
                },
                template_text={
                    "name":     "organizations/emails/organization_newsletter.txt",
                    "context":  {
                        "user":                 subscriber,
                        "organization":         self,
                        "organization_link":    self.public_url(request),
                        "newsletter":           newsletter,
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
                    subscriber.email,
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
        #            MEDIA_ROOT/organizations/<id>/avatars/<filename>
        #
        # --- As long as the uploading Path is being generated before
        #     the Organization Instance gets assigned with the unique ID,
        #     the uploading Path for the brand new Organization looks like:
        #
        #            MEDIA_ROOT/organizations/None/avatars/<filename>
        #
        # --- To fix this:
        #     1. Open the Avatar File in the Path;
        #     2. Assign the Avatar File Content to the Organization Avatar Object;
        #     3. Save the Organization Instance. Now the Avatar Image in the
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


# -----------------------------------------------------------------------------
# --- ORGANIZATION STAFF
# -----------------------------------------------------------------------------
class OrganizationStaffManager(models.Manager):
    """Organization Staff Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(OrganizationStaffManager, self).get_queryset()


@autoconnect
class OrganizationStaff(
        AttachmentMixin, CommentMixin, RatingMixin, ViewMixin,
        TimeStampedModel):
    """Organization Staff Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="organization_staff_members_created",
        verbose_name=_("Author"),
        help_text=_("Organization Staff Member Author"))
    organization = models.ForeignKey(
        Organization,
        db_index=True,
        related_name="organization_staff_members",
        verbose_name=_("Organization"),
        help_text=_("Organization"))
    member = models.ForeignKey(
        User,
        db_index=True,
        null=True, blank=True,
        related_name="organization_staff_member",
        verbose_name=_("Staff Member"),
        help_text=_("Organization Staff Member"))
    position = models.CharField(
        db_index=True,
        max_length=200, blank=True, null=True,
        verbose_name=_("Position"),
        help_text=_("Position"))
    bio = models.TextField(
        null=True, blank=True,
        verbose_name=_("Bio"),
        help_text=_("Short Bio"))

    order = models.PositiveIntegerField(
        default=0)

    # -------------------------------------------------------------------------
    # --- Social Links

    objects = OrganizationStaffManager()

    class Meta:
        verbose_name = _("organization staff member")
        verbose_name_plural = _("organization staff members")
        ordering = ["order", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.member.get_full_name())

    def __unicode__(self):
        """Docstring."""
        return u"%s: %s" % (
            self.organization.name,
            self.member.get_full_name())

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


@autoconnect
class OrganizationStaffMixin(object):
    """Organization Staff Mixin Class."""

    # -------------------------------------------------------------------------
    # --- Views
    @property
    def staff_member_organizations(self):
        """Docstring."""
        organizations = Organization.objects.filter(
            pk__in=OrganizationStaff.objects.filter(
                member=self.user,
            ).values_list(
                "organization_id", flat=True
            ),
            is_deleted=False,
        )

        return organizations

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
# --- ORGANIZATION GROUP
# -----------------------------------------------------------------------------
class OrganizationGroupManager(models.Manager):
    """Organization Group Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(OrganizationGroupManager, self).get_queryset()


@autoconnect
class OrganizationGroup(
        AttachmentMixin, CommentMixin, RatingMixin, ViewMixin,
        TimeStampedModel):
    """Organization Group Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    author = models.ForeignKey(
        User,
        db_index=True,
        related_name="organization_group_author",
        verbose_name=_("Author"),
        help_text=_("Organization Group Author"))
    name = models.CharField(
        db_index=True,
        max_length=80,
        verbose_name=_("Name"),
        help_text=_("Organiztion Group Name"))
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("Description"),
        help_text=_("Organization Group Description"))
    organization = models.ForeignKey(
        Organization,
        db_index=True,
        related_name="organization_groups",
        verbose_name=_("Organization"),
        help_text=_("Organization"))
    members = models.ManyToManyField(
        User,
        db_index=True,
        blank=True,
        related_name="organization_group_members",
        verbose_name=_("Group Member"),
        help_text=_("Organization Group Member"))

    # -------------------------------------------------------------------------
    # --- Social Links

    objects = OrganizationGroupManager()

    class Meta:
        verbose_name = _("organization group")
        verbose_name_plural = _("organization groups")
        ordering = ["-created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.organization.name,
            self.name)

    def __unicode__(self):
        """Docstring."""
        return u"%s: %s" % (
            self.organization.name,
            self.name)

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
            "organization-details", kwargs={
                "slug":     self.organization.slug,
            })
        organization_link = u"http://{domain}{url}".format(
            domain=DOMAIN_NAME,
            url=url,
            )

        return organization_link

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
class OrganizationGroupMixin(object):
    """Organization Group Mixin Class."""

    # -------------------------------------------------------------------------
    # --- Views
    @property
    def group_member_organizations(self):
        """Docstring."""
        organizations = Organization.objects.filter(
            pk__in=self.user.organization_group_members.all().values_list(
                "organization_id", flat=True
            ),
            is_deleted=False,
        )

        return organizations

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
