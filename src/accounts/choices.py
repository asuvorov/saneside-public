from django.utils.translation import ugettext_lazy as _

from core import enum


# -----------------------------------------------------------------------------
# --- GENDER TYPE CHOICES
# -----------------------------------------------------------------------------
GENDER_TYPE = enum(
    FEMALE="0",
    MALE="1",
    OTHER="2",
)
gender_choices = [
    (GENDER_TYPE.FEMALE,    _("Female")),
    (GENDER_TYPE.MALE,      _("Male")),
    (GENDER_TYPE.OTHER,     _("Other")),
]


# -----------------------------------------------------------------------------
# --- PRIVACY MODE CHOICES
# -----------------------------------------------------------------------------
PRIVACY_MODE = enum(
    PARANOID="0",
    NORMAL="1",
)
privacy_choices = [
    (PRIVACY_MODE.PARANOID, _("Paranoid")),
    (PRIVACY_MODE.NORMAL,   _("Normal")),
]


# -----------------------------------------------------------------------------
# --- WHO CAN SEE <...> CHOICES
# -----------------------------------------------------------------------------
WHO_CAN_SEE_MEMBERS = enum(
    NO_ONE="0",
    REGISTERED="1",
    CHL_MEMBERS="2",
    ORG_MEMBERS="4",
    EVERYONE="8",
)
who_can_see_members_choices = [
    (WHO_CAN_SEE_MEMBERS.NO_ONE,        _("No-one")),
    (WHO_CAN_SEE_MEMBERS.REGISTERED,    _("Registered Users")),
    (WHO_CAN_SEE_MEMBERS.CHL_MEMBERS,   _("Participants of the Challenges, I participate in too")),
    (WHO_CAN_SEE_MEMBERS.ORG_MEMBERS,   _("Staff/Group Members of the Organization(s), I affiliated with")),
    (WHO_CAN_SEE_MEMBERS.EVERYONE,      _("Everyone")),
]

WHO_CAN_SEE_ADMINS = enum(
    NO_ONE="0",
    PARTICIPATED="1",
    ALL="2",
)
who_can_see_admins_choices = [
    (WHO_CAN_SEE_ADMINS.NO_ONE,         _("No-one")),
    (WHO_CAN_SEE_ADMINS.PARTICIPATED,   _("Admins of the Challenges, I participate(-d) in")),
    (WHO_CAN_SEE_ADMINS.ALL,            _("Admins of the upcoming Challenges on the Platform")),
]
