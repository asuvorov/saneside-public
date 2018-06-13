from django.conf.urls import url

from .views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Accounts
    # -------------------------------------------------------------------------
    # --- Email
    url(r"^email/update/$",
        email_update,
        name="api-email-update"),

    # --- Password
    url(r"^password/notify/$",
        forgot_password_notify,
        name="api-forgot-password-notify"),
]
