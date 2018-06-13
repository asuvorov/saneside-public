import inspect

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geoip import GeoIP
from django.contrib.sitemaps import ping_google
from django.core.files import File
from django.core.files.storage import default_storage as storage
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields.json import JSONField
from django_extensions.db.models import TimeStampedModel

import papertrail
import pendulum

from termcolor import colored

from api.sendgrid_api import send_templated_email
from app.utils import update_seo_model_instance_metadata
from accounts.choices import (
    GENDER_TYPE, gender_choices,
    WHO_CAN_SEE_MEMBERS, who_can_see_members_choices,
    WHO_CAN_SEE_ADMINS, who_can_see_admins_choices,
    )
from challenges.models import (
    ChallengeMixin,
    ParticipationMixin,
    )
from core.decorators import autoconnect
from core.models import (
    Address,
    CommentMixin,
    ComplaintMixin,
    Phone,
    RatingMixin,
    ViewMixin,
    )
from core.utils import (
    get_client_ip,
    get_unique_filename,
    )
from organizations.models import (
    OrganizationStaffMixin,
    OrganizationGroupMixin,
    )


# -----------------------------------------------------------------------------
# --- USER PROFILE
# -----------------------------------------------------------------------------
def user_directory_path(instance, filename):
    """User Directory Path."""
    # --- File will be uploaded to
    #     MEDIA_ROOT/accounts/<id>/avatars/<filename>
    return "accounts/{id}/avatars/{fname}".format(
        id=instance.user.id,
        fname=get_unique_filename(
            filename.split("/")[-1]
            ))


class UserProfileManager(models.Manager):
    """User Profile Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(UserProfileManager, self).get_queryset()


@autoconnect
class UserProfile(
        CommentMixin, ComplaintMixin,
        ChallengeMixin, ParticipationMixin,
        OrganizationGroupMixin, OrganizationStaffMixin,
        RatingMixin, ViewMixin, TimeStampedModel):
    """User Profile Model."""

    # TODO: For each Model define the Attributes and Methods in this Order:
    #       Relations
    #       Attributes - Mandatory
    #       Attributes - Optional
    #       Object Manager
    #       Custom Properties
    #       Methods
    #       Meta and String

    # -------------------------------------------------------------------------
    # --- Basics
    user = models.OneToOneField(
        User,
        db_index=True,
        related_name="profile",
        verbose_name=_("User"),
        help_text=_("User"))
    avatar = models.ImageField(
        upload_to=user_directory_path, blank=True)
    nickname = models.CharField(
        db_index=True,
        max_length=32, null=True, blank=True,
        default="",
        verbose_name=_("Nickname"),
        help_text=_("User Nickname"))
    bio = models.TextField(
        null=True, blank=True,
        default="",
        verbose_name="Bio",
        help_text=_("User Bio"))

    gender = models.CharField(
        max_length=2,
        choices=gender_choices, default=GENDER_TYPE.FEMALE,
        verbose_name=_("Gender"),
        help_text=_("User Gender"))
    birth_day = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Birthday"),
        help_text=_("User Birthday"))

    # -------------------------------------------------------------------------
    # --- Address & Phone Number.
    address = models.ForeignKey(
        Address,
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Address"),
        help_text=_("User Address"))
    phone_number = models.ForeignKey(
        Phone,
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Phone Numbers"),
        help_text=_("User Phone Numbers"))

    # -------------------------------------------------------------------------
    # --- Flags.
    receive_newsletters = models.BooleanField(
        default=False,
        verbose_name=_("I would like to receive Email Updates"),
        help_text=_("I would like to receive Email Updates"))

    is_newly_created = models.BooleanField(
        default=True)

    # -------------------------------------------------------------------------
    # --- Different.
    fb_profile = models.CharField(
        max_length=255, null=True, blank=True)

    USERNAME_FIELD = "email"

    objects = UserProfileManager()

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")
        ordering = [
            "user__first_name",
            "user__last_name",
        ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.user)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.user.get_full_name()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Profile direct URL.
    def public_url(self, request=None):
        """Docstring."""
        if request:
            DOMAIN_NAME = request.get_host()
        else:
            DOMAIN_NAME = settings.DOMAIN_NAME

        url = reverse(
            "profile-view", kwargs={
                "user_id":  self.user_id,
            })
        profile_link = u"http://{domain}{url}".format(
            domain=DOMAIN_NAME,
            url=url,
            )

        return profile_link

    def get_absolute_url(self):
        """Method to be called by Django Sitemap Framework."""
        url = reverse(
            "profile-view", kwargs={
                "user_id":  self.user_id,
            })

        return url

    # -------------------------------------------------------------------------
    # --- Profile Completeness.
    @property
    def grace_period_days_left(self):
        """Docstring."""
        dt = pendulum.today() - self.created

        if dt.days >= settings.PROFILE_COMPLETENESS_GRACE_PERIOD:
            return 0

        return settings.PROFILE_COMPLETENESS_GRACE_PERIOD - dt.days

    @property
    def is_completed(self):
        """Docstring."""
        return self.completeness_total >= 80 or self.grace_period_days_left > 0

    @property
    def completeness_total(self):
        """Return Profile Completeness."""
        completeness_user = (
            int(bool(self.user.username)) +
            int(bool(self.user.first_name)) +
            int(bool(self.user.last_name)) +
            int(bool(self.user.email))
        )

        completeness_profile = (
            int(bool(self.avatar)) +
            int(bool(self.nickname)) +
            int(bool(self.bio)) +
            int(bool(self.gender)) +
            int(bool(self.birth_day))
        )

        completeness_address = 0
        if self.address:
            completeness_address = (
                int(bool(self.address.address_1)) +
                int(bool(self.address.city)) +
                int(bool(self.address.zip_code)) +
                int(bool(self.address.province)) +
                int(bool(self.address.country))
            )

        completeness_phone = 0
        if self.phone_number:
            completeness_phone = (
                int(bool(self.phone_number.phone_number)) +
                int(bool(self.phone_number.mobile_phone_number))
            )

        completeness_total = int(((
            completeness_user +
            completeness_profile +
            completeness_address +
            completeness_phone
        ) / 16.0) * 100)

        return completeness_total

    # -------------------------------------------------------------------------
    # --- Helpers.
    @property
    def stat_gender_name(self):
        """Docstring."""
        for code, name in gender_choices:
            if self.gender == code:
                return name.lower()

        return ""

    @property
    def full_name_straight(self):
        """Docstring."""
        return self.user.first_name + " " + self.user.last_name

    @property
    def full_name(self):
        """Docstring."""
        return self.user.last_name + ", " + self.user.first_name

    @property
    def short_name(self):
        """Docstring."""
        try:
            return self.user.first_name + " " + self.user.last_name[0] + "."
        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

            return self.user.first_name

    @property
    def auth_name(self):
        """Docstring."""
        try:
            if self.short_name:
                return self.short_name
            elif self.nickname:
                return self.nickname
            else:
                return self.user.email.split("@")[0]
        except:
            pass

        return "------"

    @property
    def name(self):
        """Docstring."""
        return self.user.get_full_name()

    # -------------------------------------------------------------------------
    # --- Challenges

    # -------------------------------------------------------------------------
    # --- Methods
    def email_notify_signup_confirmation(self, request=None, url=None):
        """Send Notification to the User."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content.
        greetings = _(
            "Dear, %(name)s.") % {
                "name":     self.user.first_name,
            }
        htmlbody = _(
            "<p>To finish your registration Process, please, follow this \"<a href=\"%(confirmation_link)s\">Link</a>\".</p>") % {
                "confirmation_link":    url,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "accounts/emails/account_signup_confirmation_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "accounts/emails/account_signup_confirmation.txt",
                "context":  {
                    "user":                 self.user,
                    "confirmation_link":    url,
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

    def email_notify_signup_confirmed(self, request=None, url=None):
        """Send Notification to the User."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # ---  Render HTML Email Content.
        greetings = _(
            "Dear, %(name)s.") % {
                "name":     self.user.first_name,
            }
        htmlbody = _(
            "<p>Your Account was successfully confirmed.</p>"
            "<p>To log-in, please, follow this \"<a href=\"%(login_link)s\">Link</a>\".</p>") % {
                "login_link":   url,
            }

        # --- Send Email.
        send_templated_email(
            template_subj={
                "name":     "accounts/emails/account_signup_confirmed_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "accounts/emails/account_signup_confirmed.txt",
                "context":  {
                    "user":         self.user,
                    "login_link":   url,
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

    def email_notify_password_reset(self, request=None, url=None):
        """Send Notification to the User."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # ---  Render HTML Email Content.
        greetings = _(
            "Dear, %(name)s.") % {
                "name":     self.user.first_name,
            }
        htmlbody = _(
            "<p>You are about to restore your Password on SaneSide.</p>"
            "<p>To proceed, please, follow this \"<a href=\"%(confirmation_link)s\">Link</a>\".</p>") % {
                "confirmation_link":    url,
            }

        # --- Send Email.
        send_templated_email(
            template_subj={
                "name":     "accounts/emails/account_forgot_password_notify_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "accounts/emails/account_forgot_password_notify.txt",
                "context":  {
                    "user":                 self.user,
                    "confirmation_link":    url,
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

    def email_notify_password_changed(self, request=None, url=None):
        """Send Notification to the User."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content.
        greetings = _(
            "Dear, %(name)s.") % {
                "name":     request.user.first_name,
            }
        htmlbody = _(
            "<p>You have successfully reset the Password from your Account.</p>"
            "<p>To log-in, please, follow this \"<a href=\"%(login_link)s\">Link</a>\".</p>") % {
                "login_link":   url,
            }

        # --- Send Email.
        send_templated_email(
            template_subj={
                "name":     "accounts/emails/account_successful_password_reset_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "accounts/emails/account_successful_password_reset.txt",
                "context":  {
                    "user":         self.user,
                    "login_link":   url,
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

    # -------------------------------------------------------------------------
    # --- Methods.
    def image_tag(self):
        """Render Avatar Thumbnail."""
        if self.avatar:
            return u"<img src='{url}' width='{width}' height='{height}' />".format(
                url=self.avatar.url,
                width=100,
                height=100,
                )
        else:
            return "(Sin Imagen)"

    image_tag.short_description = "Avatar"
    image_tag.allow_tags = True

    # -------------------------------------------------------------------------
    # --- Signals.
    def pre_save(self, **kwargs):
        """Docstring."""
        pass

    def post_save(self, created, **kwargs):
        """Docstring."""
        # ---------------------------------------------------------------------
        # --- Ping Google.
        try:
            ping_google()
        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

        # ---------------------------------------------------------------------
        # --- Update/insert SEO Model Instance Metadata.
        update_seo_model_instance_metadata(
            title=self.user.get_full_name(),
            description=self.bio,
            keywords=self.nickname,
            heading=self.user.get_full_name(),
            path=self.get_absolute_url(),
            object_id=self.id,
            content_type_id=ContentType.objects.get_for_model(self).id,
        )

        # ---------------------------------------------------------------------
        # --- The Path for uploading Avatar Images is:
        #
        #            MEDIA_ROOT/accounts/<id>/avatars/<filename>
        #
        # --- As long as the uploading Path is being generated before
        #     the Profile Instance gets assigned with the unique ID,
        #     the uploading Path for the brand new Profile looks like:
        #
        #            MEDIA_ROOT/accounts/None/avatars/<filename>
        #
        # --- To fix this:
        #     1. Open the Avatar File in the Path;
        #     2. Assign the Avatar File Content to the Profile Avatar Object;
        #     3. Save the Profile Instance. Now the Avatar Image in the
        #        correct Path;
        #     4. Delete previous Avatar File;
        #
        try:
            if created:
                avatar = File(storage.open(self.avatar.file.name, "rb"))

                self.avatar = avatar
                self.save()

                storage.delete(avatar.file.name)
        except:
            pass

    def pre_delete(self, **kwargs):
        """Docstring."""
        pass

    def post_delete(self, **kwargs):
        """Docstring."""
        pass


# -----------------------------------------------------------------------------
# --- USER PRIVACY GENERAL
# -----------------------------------------------------------------------------
class UserPrivacyGeneralManager(models.Manager):
    """User Privacy (general) Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(UserPrivacyGeneralManager, self).get_queryset()


@autoconnect
class UserPrivacyGeneral(TimeStampedModel):
    """User Privacy (general) Model."""

    # -------------------------------------------------------------------------
    # --- Basics.
    user = models.OneToOneField(
        User,
        db_index=True,
        related_name="privacy_general",
        verbose_name=_("User"),
        help_text=_("User"))

    # -------------------------------------------------------------------------
    # --- Flags.
    hide_profile_from_search = models.BooleanField(
        default=False,
        verbose_name=_("Hide my Profile from the Search Results"),
        help_text=_("Hide my Profile from the Search Results"))
    hide_profile_from_list = models.BooleanField(
        default=False,
        verbose_name=_("Hide my Profile from the Members' List"),
        help_text=_("Hide my Profile from the Members' List"))

    objects = UserPrivacyGeneralManager()

    class Meta:
        verbose_name = _("user privacy (general)")
        verbose_name_plural = _("user privacy (general)")
        ordering = [
            "user__first_name",
            "user__last_name",
        ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.user)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.user.get_full_name()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Signals.
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
# --- USER PRIVACY MEMBERS
# -----------------------------------------------------------------------------
class UserPrivacyMembersManager(models.Manager):
    """User Privacy (Members) Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(UserPrivacyMembersManager, self).get_queryset()


@autoconnect
class UserPrivacyMembers(TimeStampedModel):
    """User Privacy (Members) Model."""

    # -------------------------------------------------------------------------
    # --- Basics.
    user = models.OneToOneField(
        User,
        db_index=True,
        related_name="privacy_members",
        verbose_name=_("User"),
        help_text=_("User"))

    # -------------------------------------------------------------------------
    # --- Flags.
    profile_details = models.CharField(
        max_length=2,
        choices=who_can_see_members_choices,
        default=WHO_CAN_SEE_MEMBERS.REGISTERED,
        verbose_name=_(
            "Who can see my Profile Details (e.g. Avatar, Name, Bio, Gender, Birthday)"),
        help_text=_(
            "Who can see my Profile Details (e.g. Avatar, Name, Bio, Gender, Birthday)"))
    contact_details = models.CharField(
        max_length=2,
        choices=who_can_see_members_choices,
        default=WHO_CAN_SEE_MEMBERS.NO_ONE,
        verbose_name=_(
            "Who can see my Contact Details (e.g. Address, Phone #, Email)"),
        help_text=_(
            "Who can see my Contact Details (e.g. Address, Phone #, Email)"))

    challenges_upcoming = models.CharField(
        max_length=2,
        choices=who_can_see_members_choices,
        default=WHO_CAN_SEE_MEMBERS.CHL_MEMBERS,
        verbose_name=_(
            "Who can see the List of Challenges, I'm going to participate in (upcoming Challenges)"),
        help_text=_(
            "Who can see the List of Challenges, I'm going to participate in (upcoming Challenges)"))
    challenges_completed = models.CharField(
        max_length=2,
        choices=who_can_see_members_choices,
        default=WHO_CAN_SEE_MEMBERS.CHL_MEMBERS,
        verbose_name=_(
            "Who can see the List of Challenges, I participated in (completed Challenges)"),
        help_text=_(
            "Who can see the List of Challenges, I participated in (completed Challenges)"))

    challenges_affiliated = models.CharField(
        max_length=2,
        choices=who_can_see_members_choices,
        default=WHO_CAN_SEE_MEMBERS.REGISTERED,
        verbose_name=_(
            "Who can see the List of Challenges, I affiliated with "),
        help_text=_(
            "Who can see the List of Challenges, I affiliated with "))

    participations_canceled = models.CharField(
        max_length=2,
        choices=who_can_see_members_choices,
        default=WHO_CAN_SEE_MEMBERS.ORG_MEMBERS,
        verbose_name=_(
            "Who can see the List of Participations, canceled by me (withdrawn Participations)"),
        help_text=_(
            "Who can see the List of Participations, canceled by me (withdrawn Participations)"))
    participations_rejected = models.CharField(
        max_length=2,
        choices=who_can_see_members_choices,
        default=WHO_CAN_SEE_MEMBERS.ORG_MEMBERS,
        verbose_name=_(
            "Who can see the List of Participations, canceled by the Challenge Organizer/Admin (rejected Participations)"),
        help_text=_(
            "Who can see the List of Participations, canceled by the Challenge Organizer/Admin (rejected Participations)"))

    objects = UserPrivacyMembersManager()

    class Meta:
        verbose_name = _("user privacy (members)")
        verbose_name_plural = _("user privacy (members)")
        ordering = [
            "user__first_name",
            "user__last_name",
        ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.user)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.user.get_full_name()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Signals.
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
# --- USER PRIVACY ADMINS
# -----------------------------------------------------------------------------
class UserPrivacyAdminsManager(models.Manager):
    """User Privacy (Admins) Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(UserPrivacyAdminsManager, self).get_queryset()


@autoconnect
class UserPrivacyAdmins(TimeStampedModel):
    """User Privacy (Admins) Model."""

    # -------------------------------------------------------------------------
    # --- Basics.
    user = models.OneToOneField(
        User,
        db_index=True,
        related_name="privacy_admins",
        verbose_name=_("User"),
        help_text=_("User"))

    # -------------------------------------------------------------------------
    # --- Flags.
    profile_details = models.CharField(
        max_length=2,
        choices=who_can_see_admins_choices,
        default=WHO_CAN_SEE_ADMINS.ALL,
        verbose_name=_(
            "Who can see my Profile Details (e.g. Avatar, Name, Bio, Gender, Birthday)"),
        help_text=_(
            "Who can see my Profile Details (e.g. Avatar, Name, Bio, Gender, Birthday)"))
    contact_details = models.CharField(
        max_length=2,
        choices=who_can_see_admins_choices,
        default=WHO_CAN_SEE_ADMINS.NO_ONE,
        verbose_name=_(
            "Who can see my Contact Details (e.g. Address, Phone #, Email)"),
        help_text=_(
            "Who can see my Contact Details (e.g. Address, Phone #, Email)"))

    challenges_upcoming = models.CharField(
        max_length=2,
        choices=who_can_see_admins_choices,
        default=WHO_CAN_SEE_ADMINS.ALL,
        verbose_name=_(
            "Who can see the List of Challenges, I'm going to participate in (upcoming Challenges)"),
        help_text=_(
            "Who can see the List of Challenges, I'm going to participate in (upcoming Challenges)"))
    challenges_completed = models.CharField(
        max_length=2,
        choices=who_can_see_admins_choices,
        default=WHO_CAN_SEE_ADMINS.ALL,
        verbose_name=_(
            "Who can see the List of Challenges, I participated in (completed Challenges)"),
        help_text=_(
            "Who can see the List of Challenges, I participated in (completed Challenges)"))

    challenges_affiliated = models.CharField(
        max_length=2,
        choices=who_can_see_admins_choices,
        default=WHO_CAN_SEE_ADMINS.ALL,
        verbose_name=_(
            "Who can see the List of Challenges, I affiliated with "),
        help_text=_(
            "Who can see the List of Challenges, I affiliated with "))

    participations_canceled = models.CharField(
        max_length=2,
        choices=who_can_see_admins_choices,
        default=WHO_CAN_SEE_ADMINS.PARTICIPATED,
        verbose_name=_(
            "Who can see the List of Participations, canceled by me (withdrawn Participations)"),
        help_text=_(
            "Who can see the List of Participations, canceled by me (withdrawn Participations)"))
    participations_rejected = models.CharField(
        max_length=2,
        choices=who_can_see_admins_choices,
        default=WHO_CAN_SEE_ADMINS.PARTICIPATED,
        verbose_name=_(
            "Who can see the List of Participations, canceled by the Challenge Organizer/Admin (rejected Participations)"),
        help_text=_(
            "Who can see the List of Participations, canceled by the Challenge Organizer/Admin (rejected Participations)"))

    objects = UserPrivacyAdminsManager()

    class Meta:
        verbose_name = _("user privacy (admins)")
        verbose_name_plural = _("user privacy (admins)")
        ordering = [
            "user__first_name",
            "user__last_name",
        ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.user)

    def __unicode__(self):
        """Docstring."""
        return u"%s" % self.user.get_full_name()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Signals.
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
# --- USER LOGIN STATISTICS
# -----------------------------------------------------------------------------
class UserLoginManager(models.Manager):
    """User Login Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(UserLoginManager, self).get_queryset()

    def insert(self, request, user=None, provider="Desktop", **extra_fields):
        """Docstring."""
        try:
            g = GeoIP()
            ip = get_client_ip(request)

            if not user:
                user = request.user

            login = self.model(
                user=user,
                ip=ip,
                provider=provider,
                country=g.country(ip),
                city=g.city(ip),
                **extra_fields
            )
            login.save(using=self._db)

            return login

        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

            # -----------------------------------------------------------------
            # --- Save the Log.
            papertrail.log(
                event_type="exception-insert-user-login",
                message="Exception: Insert User Login Entry",
                data={
                    "user":         user if user else request.user.email,
                    "message":      str(e),
                },
                # timestamp=timezone.now(),
                targets={
                    "user":         user if user else request.user,
                },
                )


@autoconnect
class UserLogin(TimeStampedModel):
    """User Login Model."""

    # -------------------------------------------------------------------------
    # --- Basics.
    user = models.ForeignKey(
        User,
        db_index=True,
        related_name="user_login",
        verbose_name=_("User"),
        help_text=_("User"))
    ip = models.CharField(
        db_index=True,
        max_length=16,
        verbose_name=_("IP"),
        help_text=_("User IP Address"))
    provider = models.CharField(
        max_length=64,
        default="Desktop",
        verbose_name=_("Provider"),
        help_text=_("User Internet Provider"))

    # -------------------------------------------------------------------------
    # --- Geolocation.
    country = JSONField(
        null=True, blank=True)
    city = JSONField(
        null=True, blank=True)

    objects = UserLoginManager()

    class Meta:
        verbose_name = _("user login")
        verbose_name_plural = _("user logins")
        ordering = ["-created", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.id,
            self.user)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Signals.
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
# --- TEAM
# -----------------------------------------------------------------------------
class TeamManager(models.Manager):
    """Team Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(TeamManager, self).get_queryset()


@autoconnect
class Team(TimeStampedModel):
    """Team Model."""

    # -------------------------------------------------------------------------
    # --- Basics.
    name = models.CharField(
        db_index=True,
        max_length=200,
        verbose_name=_("Team"),
        help_text=_("Team Name"))
    order = models.PositiveIntegerField(
        default=0)

    objects = TeamManager()

    class Meta:
        verbose_name = _("team")
        verbose_name_plural = _("teams")
        ordering = ["order", ]

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
    # --- Signals.
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
# --- TEAM MEMBER
# -----------------------------------------------------------------------------
class TeamMemberManager(models.Manager):
    """Team Member Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(TeamMemberManager, self).get_queryset()


@autoconnect
class TeamMember(TimeStampedModel):
    """Team Member Model."""

    # -------------------------------------------------------------------------
    # --- Basics.
    user = models.OneToOneField(
        User,
        db_index=True,
        related_name="team_member",
        verbose_name=_("Team Member"),
        help_text=_("Team Member"))
    team = models.ForeignKey(
        Team,
        db_index=True,
        null=True, blank=True,
        related_name="members",
        verbose_name=_("Team"),
        help_text=_("Team"))

    position = models.CharField(
        db_index=True,
        max_length=200, null=True, blank=True,
        verbose_name=_("Position"),
        help_text=_("Team Member Position"))
    order = models.PositiveIntegerField(
        default=0)

    objects = TeamMemberManager()

    class Meta:
        verbose_name = _("team member")
        verbose_name_plural = _("team members")
        ordering = ["order", ]

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s' in %s)>" % (
            self.__class__.__name__,
            self.id,
            self.user,
            self.team)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    # -------------------------------------------------------------------------
    # --- Methods.
    def image_tag(self):
        """Render Avatar Thumbnail."""
        if self.user.profile.avatar:
            return u"<img src='{url}' width='{width}' height='{height}' />".format(
                url=self.user.profile.avatar.url,
                width=100,
                height=100,
                )
        else:
            return "(Sin Imagen)"

    image_tag.short_description = "Avatar"
    image_tag.allow_tags = True

    # -------------------------------------------------------------------------
    # --- Signals.
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
