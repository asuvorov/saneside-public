from django.conf.urls import url

from blog.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Desktop
    # -------------------------------------------------------------------------
    # --- Post List
    url(r"^$",
        post_list,
        name="post-list"),
    # url(r"^posts/(?P<year>[0-9]{4})/$",
    #     post_year_archive,
    #     name="post-year-archive"),
    # url(r"^posts/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$",
    #     post_month_archive,
    #     name="post-month-archive"),
    # url(r"^posts/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$",
    #     post_day_archive,
    #     name="post-day-archive"),

    # -------------------------------------------------------------------------
    # --- Post create
    url(r"^create/$",
        post_create,
        name="post-create"),

    # -------------------------------------------------------------------------
    # --- Post view/edit
    url(r"^(?P<slug>[\w_-]+)/$",
        post_details,
        name="post-details"),
    url(r"^(?P<slug>[\w_-]+)/edit/$",
        post_edit,
        name="post-edit"),
]
