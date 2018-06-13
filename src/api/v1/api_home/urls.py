from django.conf.urls import url

from .views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Home
    # -------------------------------------------------------------------------
    # --- FAQ
    url(r"^faqs/(?P<faq_id>[\w_-]+)/$",
        faq_details,
        name="api-faq-details"),

    # -------------------------------------------------------------------------
    # --- Contact us
    url(r"^contact-us/$",
        contact_us,
        name="api-contact-us"),
]
