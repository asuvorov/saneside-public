from django.conf.urls import url

from .views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Challenges
    # -------------------------------------------------------------------------
    # --- Calendar Actions
    url(r"^upcoming/$",
        challenge_upcoming,
        name="api-challenge-upcoming"),

    # -------------------------------------------------------------------------
    # --- Admin actions
    url(r"^(?P<challenge_id>[\w_-]+)/create/$",
        challenge_create,
        name="api-challenge-create"),
    url(r"^(?P<challenge_id>[\w_-]+)/complete/$",
        challenge_complete,
        name="api-challenge-complete"),
    url(r"^(?P<challenge_id>[\w_-]+)/clone/$",
        challenge_clone,
        name="api-challenge-clone"),
    url(r"^(?P<challenge_id>[\w_-]+)/close/$",
        challenge_close,
        name="api-challenge-close"),

    # -------------------------------------------------------------------------
    # --- Participations
    # -------------------------------------------------------------------------
    # --- User actions
    url(r"^(?P<challenge_id>[\w_-]+)/participation/post/$",
        participation_post,
        name="api-participation-post"),
    url(r"^(?P<challenge_id>[\w_-]+)/participation/withdraw/$",
        participation_withdraw,
        name="api-participation-withdraw"),

    # -------------------------------------------------------------------------
    # --- Admin actions
    url(r"^(?P<challenge_id>[\w_-]+)/participation/remove/$",
        participation_remove,
        name="api-participation-remove"),

    url(r"^(?P<challenge_id>[\w_-]+)/participation/accept-app/$",
        participation_accept_application,
        name="api-participation-accept-application"),
    url(r"^(?P<challenge_id>[\w_-]+)/participation/reject-app/$",
        participation_reject_application,
        name="api-participation-reject-application"),

    # -------------------------------------------------------------------------
    # --- Experience Reports
    # -------------------------------------------------------------------------
    # --- User actions
    url(r"^(?P<challenge_id>[\w_-]+)/submit-sr/$",
        challenge_selfreflection_submit,
        name="api-challenge-selfreflection-submit"),

    # -------------------------------------------------------------------------
    # --- Admin actions
    url(r"^(?P<challenge_id>[\w_-]+)/participation/accept-sr/$",
        participation_accept_selfreflection,
        name="api-participation-accept-selfreflection"),
    url(r"^(?P<challenge_id>[\w_-]+)/participation/reject-sr/$",
        participation_reject_selfreflection,
        name="api-participation-reject-selfreflection"),
]
