from django.conf.urls import url

from .views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Core
    # -------------------------------------------------------------------------
    # --- Comments
    url(r"^comments/$",
        comment_list,
        name="api-comment-list"),
    url(r"^comments/(?P<comment_id>[\w_-]+)/$",
        comment_details,
        name="api-comment-details"),

    # --- Complaints
    url(r"^complaints/$",
        complaint_list,
        name="api-complaint-list"),

    # --- Ratings
    url(r"^ratings/$",
        rating_list,
        name="api-rating-list"),
    url(r"^ratings/(?P<rating_id>[\w_-]+)/$",
        rating_details,
        name="api-rating-details"),
]
