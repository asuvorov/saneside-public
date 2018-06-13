from django.utils.translation import ugettext_lazy as _

from core import enum


# -----------------------------------------------------------------------------
# --- SOCIAL LINKS CHOICES
# -----------------------------------------------------------------------------
SOCIAL_APP = enum(
    NONE="--------",
    FACEBOOK="0",
    TWITTER="1",
    LINKEDIN="2",
    GOOGLE="4",
    PINTEREST="8",
    INSTAGRAM="16",
    TUMBLR="32",
    YOUTUBE="64",
    )
social_app_choices = [
    (SOCIAL_APP.NONE,       _("--------")),
    (SOCIAL_APP.FACEBOOK,   _("Facebook")),
    (SOCIAL_APP.TWITTER,    _("Twitter")),
    (SOCIAL_APP.LINKEDIN,   _("Linked In")),
    (SOCIAL_APP.GOOGLE,     _("Google +")),
    (SOCIAL_APP.PINTEREST,  _("Pinterest")),
    (SOCIAL_APP.INSTAGRAM,  _("Instagram")),
    (SOCIAL_APP.TUMBLR,     _("Tumblr")),
    (SOCIAL_APP.YOUTUBE,    _("YouTube")),
    ]

SOCIAL_APP_ICONS = enum(
    NONE="--------",
    FACEBOOK="0",
    TWITTER="1",
    LINKEDIN="2",
    GOOGLE="4",
    PINTEREST="8",
    INSTAGRAM="16",
    TUMBLR="32",
    YOUTUBE="64",
    )
social_app_icons = [
    (SOCIAL_APP_ICONS.NONE,         ""),
    (SOCIAL_APP_ICONS.FACEBOOK,     "fa fa-facebook fa-fw"),
    (SOCIAL_APP_ICONS.TWITTER,      "fa fa-twitter fa-fw"),
    (SOCIAL_APP_ICONS.LINKEDIN,     "fa fa-linkedin fa-fw"),
    (SOCIAL_APP_ICONS.GOOGLE,       "fa fa-google-plus fa-fw"),
    (SOCIAL_APP_ICONS.PINTEREST,    "fa fa-pinterest fa-fw"),
    (SOCIAL_APP_ICONS.INSTAGRAM,    "fa fa-instagram fa-fw"),
    (SOCIAL_APP_ICONS.TUMBLR,       "fa fa-tumblr fa-fw"),
    (SOCIAL_APP_ICONS.YOUTUBE,      "fa fa-youtube fa-fw"),
    ]

SOCIAL_APP_BUTTONS = enum(
    NONE="--------",
    FACEBOOK="0",
    TWITTER="1",
    LINKEDIN="2",
    GOOGLE="4",
    PINTEREST="8",
    INSTAGRAM="16",
    TUMBLR="32",
    YOUTUBE="64",
    )
social_app_buttons = [
    (SOCIAL_APP_BUTTONS.NONE,         ""),
    (SOCIAL_APP_BUTTONS.FACEBOOK,     "btn btn-facebook"),
    (SOCIAL_APP_BUTTONS.TWITTER,      "btn btn-twitter"),
    (SOCIAL_APP_BUTTONS.LINKEDIN,     "btn btn-linkedin"),
    (SOCIAL_APP_BUTTONS.GOOGLE,       "btn btn-google-plus"),
    (SOCIAL_APP_BUTTONS.PINTEREST,    "btn btn-pinterest"),
    (SOCIAL_APP_BUTTONS.INSTAGRAM,    "btn btn-instagram"),
    (SOCIAL_APP_BUTTONS.TUMBLR,       "btn btn-tumblr"),
    (SOCIAL_APP_BUTTONS.YOUTUBE,      "btn btn-youtube"),
    ]
