from django.conf.urls import url

from home.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- DESKTOP
    # -------------------------------------------------------------------------
    # --- Index
    url(r"^$",
        index,
        name="index"),

    # -------------------------------------------------------------------------
    # --- Terms & Conditions
    url(r"^privacy-policy/$",
        privacy_policy,
        name="privacy-policy"),
    url(r"^user-agreement/$",
        user_agreement,
        name="user-agreement"),

    # -------------------------------------------------------------------------
    # --- Media
    url(r"^our-team/$",
        our_team,
        name="our-team"),
    url(r"^our-partners/$",
        our_partners,
        name="our-partners"),

    # -------------------------------------------------------------------------
    # --- Feedback
    url(r"^about-us/$",
        about_us,
        name="about-us"),
    url(r"^contact-us/$",
        contact_us,
        name="contact-us"),

    # -------------------------------------------------------------------------
    # --- FAQ
    url(r"^faq/$",
        faq,
        name="faq"),
    url(r"^faq/create/$",
        faq_create,
        name="faq-create"),
    url(r"^faq/(?P<faq_id>[\w_-]+)/edit/$",
        faq_edit,
        name="faq-edit"),

    # -------------------------------------------------------------------------
    # --- Feature Test
    url(r"^feature/$",
        feature,
        name="feature"),
]
