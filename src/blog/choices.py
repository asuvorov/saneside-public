from django.utils.translation import ugettext_lazy as _

from core import enum


# -----------------------------------------------------------------------------
# --- POST STATUS CHOICES
# -----------------------------------------------------------------------------
POST_STATUS = enum(
    DRAFT="0",
    VISIBLE="1",
    CLOSED="2",
    )
post_status_choices = [
    (POST_STATUS.DRAFT,     _("Draft")),
    (POST_STATUS.VISIBLE,   _("Visible")),
    (POST_STATUS.CLOSED,    _("Closed")),
    ]
