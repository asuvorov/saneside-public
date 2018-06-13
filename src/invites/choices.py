from django.utils.translation import ugettext_lazy as _

from core import enum


# -----------------------------------------------------------------------------
# --- INVITE STATUS CHOICES
# -----------------------------------------------------------------------------
INVITE_STATUS = enum(
    NEW="0",
    ACCEPTED="1",
    REJECTED="2",
    REVOKED="4",
    )
invite_status_choices = [
    (INVITE_STATUS.NEW,         _("New")),
    (INVITE_STATUS.ACCEPTED,    _("Accepted")),
    (INVITE_STATUS.REJECTED,    _("Rejected")),
    (INVITE_STATUS.REVOKED,     _("Revoked")),
    ]
