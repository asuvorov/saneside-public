from django.conf.urls import url

from core.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Desktop

    # -------------------------------------------------------------------------
    # --- AJAX
    # --- Attachments
    url(r"^tmp-upload/$",
        tmp_upload,
        name="tmp-upload"),
    url(r"^remove-upload/$",
        remove_upload,
        name="remove-upload"),
    url(r"^remove-link/$",
        remove_link,
        name="remove-link"),
]
