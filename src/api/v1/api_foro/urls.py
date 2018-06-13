from django.conf.urls import url

from .views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Forum
    # -------------------------------------------------------------------------
    # --- Forums
    url(r"^forum/(?P<forum_id>[\w_-]+)/remove/$",
        forum_remove,
        name="api-forum-remove"),

    # -------------------------------------------------------------------------
    # --- Topics
    url(r"^topic/(?P<topic_id>[\w_-]+)/remove/$",
        topic_remove,
        name="api-topic-remove"),

    # -------------------------------------------------------------------------
    # --- Posts
    url(r"^post/(?P<post_id>[\w_-]+)/remove/$",
        post_remove,
        name="api-post-remove"),
]
