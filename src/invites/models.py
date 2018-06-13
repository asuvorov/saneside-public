import inspect

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel

from termcolor import colored

from api.sendgrid_api import send_templated_email
from core.decorators import autoconnect
from invites.choices import (
    INVITE_STATUS, invite_status_choices,
    )


# -----------------------------------------------------------------------------
# --- INVITES
# -----------------------------------------------------------------------------
class InviteManager(models.Manager):
    """Invite Manager."""

    def get_queryset(self):
        """Docstring."""
        return super(InviteManager, self).get_queryset()

    def get_all(self):
        """Docstring."""
        return self.get_queryset()

    def get_all_sent(self):
        """Docstring."""
        return self.get_queryset().filter(
            is_archived_for_inviter=False,
            )

    def get_all_received(self):
        """Docstring."""
        return self.get_queryset().filter(
            is_archived_for_invitee=False,
            )

    def get_new(self):
        """Docstring."""
        return self.get_queryset().filter(
            status=INVITE_STATUS.NEW,
        )

    def get_accepted(self):
        """Docstring."""
        return self.get_queryset().filter(
            status=INVITE_STATUS.ACCEPTED,
        )

    def get_rejected(self):
        """Docstring."""
        return self.get_queryset().filter(
            status=INVITE_STATUS.REJECTED,
        )

    def get_revoked(self):
        """Docstring."""
        return self.get_queryset().filter(
            status=INVITE_STATUS.REVOKED,
        )


@autoconnect
class Invite(TimeStampedModel):
    """Invite Model."""

    # -------------------------------------------------------------------------
    # --- Basics
    inviter = models.ForeignKey(
        User,
        db_index=True,
        related_name="inviter",
        verbose_name=_("Inviter"),
        help_text=_("Inviter"))
    invitee = models.ForeignKey(
        User,
        db_index=True,
        related_name="invitee",
        verbose_name=_("Invitee"),
        help_text=_("Invitee"))

    status = models.CharField(
        db_index=True,
        max_length=2,
        choices=invite_status_choices, default=INVITE_STATUS.NEW,
        verbose_name=_("Status"),
        help_text=_("Invite Status"))

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
    # --- Significant Texts
    invitation_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Invitation Text"),
        help_text=_("Invitation Text"))
    rejection_text = models.TextField(
        null=True, blank=True,
        verbose_name=_("Rejection Text"),
        help_text=_("Rejection"))

    # -------------------------------------------------------------------------
    # --- Significant Dates
    date_accepted = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Date accepted"),
        help_text=_("Date accepted"))
    date_rejected = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Date rejected"),
        help_text=_("Date rejected"))
    date_revoked = models.DateField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Date revoked"),
        help_text=_("Date revoked"))

    # -------------------------------------------------------------------------
    # --- Flags
    is_archived_for_inviter = models.BooleanField(
        default=False,
        verbose_name=_("Archived for Inviter"),
        help_text=_("Archived for Inviter"))
    is_archived_for_invitee = models.BooleanField(
        default=False,
        verbose_name=_("Archived for Invitee"),
        help_text=_("Archived for Invitee"))

    def __repr__(self):
        """Docstring."""
        return u"<%s (%s: '%s')>" % (
            self.__class__.__name__,
            self.content_object,
            self.invitee)

    def __unicode__(self):
        """Docstring."""
        return self.__repr__()

    def __str__(self):
        """Docstring."""
        return self.__unicode__()

    objects = InviteManager()

    class Meta:
        verbose_name = _("invite")
        verbose_name_plural = _("invites")
        ordering = ["-id", ]

    # -------------------------------------------------------------------------
    # --- Invitation Status Flags
    @property
    def is_new(self):
        """Docstring."""
        return self.status == INVITE_STATUS.NEW

    @property
    def is_accepted(self):
        """Docstring."""
        return self.status == INVITE_STATUS.ACCEPTED

    @property
    def is_rejected(self):
        """Docstring."""
        return self.status == INVITE_STATUS.REJECTED

    @property
    def is_revoked(self):
        """Docstring."""
        return self.status == INVITE_STATUS.REVOKED

    # -------------------------------------------------------------------------
    # --- Methods
    def email_notify_invitee_inv_created(self, request):
        """Send Notification to the Invitee."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.invitee.first_name,
            }
        htmlbody = _(
            "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" has invited you to %(subject)s \"<a href=\"%(url)s\">%(name)s</a>\" with the following:</p>"
            "<p>%(text)s</p>"
            "<p>Please, don\'t forget to accept, or reject Invitation.</p>") % {
                "profile":  self.inviter.profile.public_url(request),
                "member":   self.inviter.get_full_name(),
                "subject":  self.content_type.name.capitalize(),
                "url":      self.content_object.public_url(request),
                "name":     self.content_object.name,
                "text":     self.invitation_text,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "invites/emails/invite_created_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "invites/emails/invite_created_usr.txt",
                "context":  {
                    "user":     self.invitee.first_name,
                    "profile":  self.inviter.profile.public_url(request),
                    "member":   self.inviter.get_full_name(),
                    "subject":  self.content_type.name.capitalize(),
                    "url":      self.content_object.public_url(request),
                    "name":     self.content_object.name,
                    "text":     self.invitation_text,
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
                self.invitee.email,
            ],
            headers=None,
        )

    def email_notify_inviter_inv_created(self, request):
        """Send Notification to the Inviter."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.inviter.first_name,
            }
        htmlbody = _(
            "<p>You have invited Member \"<a href=\"%(profile)s\">%(member)s</a>\" to %(subject)s \"<a href=\"%(url)s\">%(name)s</a>\"!</p>") % {
                "profile":  self.invitee.profile.public_url(request),
                "member":   self.invitee.get_full_name(),
                "subject":  self.content_type.name.capitalize(),
                "url":      self.content_object.public_url(request),
                "name":     self.content_object.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "invites/emails/invite_created_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name": "   invites/emails/invite_created_adm.txt",
                "context":  {
                    "user":     self.inviter.first_name,
                    "profile":  self.invitee.profile.public_url(request),
                    "member":   self.invitee.get_full_name(),
                    "subject":  self.content_type.name.capitalize(),
                    "url":      self.content_object.public_url(request),
                    "name":     self.content_object.name,
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
                self.inviter.email,
            ],
            headers=None,
        )

    def email_notify_invitee_inv_accepted(self, request):
        """Send Notification to the Invitee."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.invitee.first_name,
            }
        htmlbody = _(
            "<p>You have accepted \"<a href=\"%(profile)s\">%(member)s\'s</a>\" Invitation to %(subject)s \"<a href=\"%(url)s\">%(name)s</a>\"!</p>") % {
                "profile":  self.inviter.profile.public_url(request),
                "member":   self.inviter.get_full_name(),
                "subject":  self.content_type.name.capitalize(),
                "url":      self.content_object.public_url(request),
                "name":     self.content_object.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "invites/emails/invite_accepted_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "invites/emails/invite_accepted_usr.txt",
                "context":  {
                    "invite":           self,
                    "profile_link":     self.inviter.profile.public_url(request),
                    "subject_link":     self.content_object.public_url(request),
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
                self.invitee.email,
            ],
            headers=None,
        )

    def email_notify_inviter_inv_accepted(self, request):
        """Send Notification to the Inviter."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.inviter.first_name,
            }
        htmlbody = _(
            "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" accepted your Invitation to %(subject)s \"<a href=\"%(url)s\">%(name)s</a>\"!</p>") % {
                "profile":  self.invitee.profile.public_url(request),
                "member":   self.invitee.get_full_name(),
                "subject":  self.content_type.name.capitalize(),
                "url":      self.content_object.public_url(request),
                "name":     self.content_object.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "invites/emails/invite_accepted_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "invites/emails/invite_accepted_adm.txt",
                "context":  {
                    "invite":           self,
                    "profile_link":     self.invitee.profile.public_url(request),
                    "subject_link":     self.content_object.public_url(request),
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
                self.inviter.email,
            ],
            headers=None,
        )

    def email_notify_invitee_inv_rejected(self, request):
        """Send Notification to the Invitee."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.invitee.first_name,
            }
        htmlbody = _(
            "<p>You have rejected \"<a href=\"%(profile)s\">%(member)s\'s</a>\" Invitation to %(subject)s \"<a href=\"%(url)s\">%(name)s</a>\"!</p>") % {
                "profile":  self.inviter.profile.public_url(request),
                "member":   self.inviter.get_full_name(),
                "subject":  self.content_type.name.capitalize(),
                "url":      self.content_object.public_url(request),
                "name":     self.content_object.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "invites/emails/invite_rejected_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "invites/emails/invite_rejected_usr.txt",
                "context":  {
                    "invite":           self,
                    "profile_link":     self.inviter.profile.public_url(request),
                    "subject_link":     self.content_object.public_url(request),
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
                self.invitee.email,
            ],
            headers=None,
        )

    def email_notify_inviter_inv_rejected(self, request):
        """Send Notification to the Inviter."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.inviter.first_name,
            }
        htmlbody = _(
            "<p>Member \"<a href=\"%(profile)s\">%(member)s</a>\" rejected your Invitation to %(subject)s \"<a href=\"%(url)s\">%(name)s</a>\" with the following:</p>"
            "<p>%(text)s</p>") % {
                "profile":  self.invitee.profile.public_url(request),
                "member":   self.invitee.get_full_name(),
                "subject":  self.content_type.name.capitalize(),
                "url":      self.content_object.public_url(request),
                "name":     self.content_object.name,
                "text":     self.rejection_text,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "invites/emails/invite_rejected_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "invites/emails/invite_rejected_adm.txt",
                "context":  {
                    "invite":           self,
                    "profile_link":     self.invitee.profile.public_url(request),
                    "subject_link":     self.content_object.public_url(request),
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
                self.inviter.email,
            ],
            headers=None,
        )

    def email_notify_invitee_inv_revoked(self, request):
        """Send Notification to the Invitee."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.invitee.first_name,
            }
        htmlbody = _(
            "<p>Member \"<a href=\"%(profile)s\">%(member)s\'s</a>\" revoked their Invitation to %(subject)s \"<a href=\"%(url)s\">%(name)s</a>\"!</p>") % {
                "profile":  self.inviter.profile.public_url(request),
                "member":   self.inviter.get_full_name(),
                "subject":  self.content_type.name.capitalize(),
                "url":      self.content_object.public_url(request),
                "name":     self.content_object.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "invites/emails/invite_revoked_usr_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "invites/emails/invite_revoked_usr.txt",
                "context":  {
                    "invite":           self,
                    "profile_link":     self.inviter.profile.public_url(request),
                    "subject_link":     self.content_object.public_url(request),
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
                self.invitee.email,
            ],
            headers=None,
        )

    def email_notify_inviter_inv_revoked(self, request):
        """Send Notification to the Inviter."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        greetings = _(
            "Dear, %(user)s.") % {
                "user":     self.inviter.first_name,
            }
        htmlbody = _(
            "<p>You revoked your Invitation of Member \"<a href=\"%(profile)s\">%(member)s</a>\" to %(subject)s \"<a href=\"%(url)s\">%(name)s</a>\"!</p>") % {
                "profile":  self.invitee.profile.public_url(request),
                "member":   self.invitee.get_full_name(),
                "subject":  self.content_type.name.capitalize(),
                "url":      self.content_object.public_url(request),
                "name":     self.content_object.name,
            }

        # ---------------------------------------------------------------------
        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "invites/emails/invite_revoked_adm_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "invites/emails/invite_revoked_adm.txt",
                "context":  {
                    "invite":           self,
                    "profile_link":     self.invitee.profile.public_url(request),
                    "subject_link":     self.content_object.public_url(request),
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
                self.inviter.email,
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
