from django.conf.urls import url

from .views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Invites
    # -------------------------------------------------------------------------
    url(r"^$",
        invite_list,
        name="api-invite"),
    url(r"^archive/all/$",
        invite_archive_all,
        name="api-invite-archive-all"),
    url(r"^(?P<invite_id>[\w_-]+)/accept/$",
        invite_accept,
        name="api-invite-accept"),
    url(r"^(?P<invite_id>[\w_-]+)/reject/$",
        invite_reject,
        name="api-invite-reject"),
    url(r"^(?P<invite_id>[\w_-]+)/revoke/$",
        invite_revoke,
        name="api-invite-revoke"),
]
