from django.conf import settings

from core.choices import (
    SOCIAL_APP, social_app_choices,
    SOCIAL_APP_ICONS, social_app_icons,
    SOCIAL_APP_BUTTONS, social_app_buttons,
    )


def pb_settings(request):
    """Docstring."""
    return {
        "product_version_full":     settings.PRODUCT_VERSION_FULL,
        "product_version_num":      settings.PRODUCT_VERSION_NUM,
        "ENVIRONMENT":              settings.ENVIRONMENT,
    }


def pb_social_links(request):
    """Docstring."""
    return {
        "PB_SOCIAL_LINKS":          settings.PB_SOCIAL_LINKS,
    }


def pb_social_link_choices(request):
    """Docstring."""
    return {
        "SOCIAL_APP":               SOCIAL_APP,
        "social_app_choices":       social_app_choices,
        "SOCIAL_APP_ICONS":         SOCIAL_APP_ICONS,
        "social_app_icons":         social_app_icons,
        "SOCIAL_APP_BUTTONS":       SOCIAL_APP_BUTTONS,
        "social_app_buttons":       social_app_buttons,
    }
