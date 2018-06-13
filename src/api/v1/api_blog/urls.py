from django.conf.urls import url

from .views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Blog
    # -------------------------------------------------------------------------
    # --- Calendar Actions
    url(r"^archive/$",
        blog_archive,
        name="api-blog-archive"),

    # -------------------------------------------------------------------------
    # --- Admin Actions
    url(r"^post/(?P<post_id>[\w_-]+)/publish/$",
        post_publish,
        name="api-post-publish"),
    url(r"^post/(?P<post_id>[\w_-]+)/close/$",
        post_close,
        name="api-post-close"),
]
