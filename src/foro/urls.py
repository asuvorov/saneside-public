from django.conf.urls import url

from foro.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- DESKTOP
    # -------------------------------------------------------------------------
    # --- Forums
    url(r"^$",
        forum_list,
        name="forum-list"),
    url(r"^create/$",
        forum_create,
        name="forum-create"),
    url(r"^(?P<forum_id>[\w_-]+)/edit/$",
        forum_edit,
        name="forum-edit"),

    # -------------------------------------------------------------------------
    # --- Topics
    url(r"^(?P<forum_id>[\w_-]+)/topics/$",
        topic_list,
        name="topic-list"),
    url(r"^(?P<forum_id>[\w_-]+)/topics/create/$",
        topic_create,
        name="topic-create"),
    url(r"^(?P<forum_id>[\w_-]+)/topics/(?P<topic_id>[\w_-]+)/edit/$",
        topic_edit,
        name="topic-edit"),

    # -------------------------------------------------------------------------
    # --- Posts
    url(r"^(?P<forum_id>[\w_-]+)/topics/(?P<topic_id>[\w_-]+)/posts/$",
        topic_post_list,
        name="topic-post-list"),
    url(r"^(?P<forum_id>[\w_-]+)/topics/(?P<topic_id>[\w_-]+)/posts/create/$",
        topic_post_create,
        name="topic-post-create"),
    url(r"^(?P<forum_id>[\w_-]+)/topics/(?P<topic_id>[\w_-]+)/posts/(?P<topic_post_id>[\w_-]+)/edit/$",
        topic_post_edit,
        name="topic-post-edit"),
    url(r"^(?P<forum_id>[\w_-]+)/topics/(?P<topic_id>[\w_-]+)/posts/(?P<topic_post_id>[\w_-]+)/reply/$",
        topic_post_reply,
        name="topic-post-reply"),
]
