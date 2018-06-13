from django.conf.urls import url

from challenges.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- DESKTOP
    # -------------------------------------------------------------------------
    # --- Challenge List
    url(r"^$",
        challenge_list,
        name="challenge-list"),
    url(r"^near-you/$",
        challenge_near_you_list,
        name="challenge-near-you-list"),
    url(r"^new/$",
        challenge_new_list,
        name="challenge-new-list"),
    url(r"^dateless/$",
        challenge_dateless_list,
        name="challenge-dateless-list"),
    url(r"^featured/$",
        challenge_featured_list,
        name="challenge-featured-list"),

    # -------------------------------------------------------------------------
    # --- Challenge Category
    url(r"^categories/$",
        challenge_category_list,
        name="challenge-category-list"),

    # -------------------------------------------------------------------------
    # --- Challenge create
    url(r"^create/$",
        challenge_create,
        name="challenge-create"),

    # -------------------------------------------------------------------------
    # --- Challenge view/edit
    url(r"^(?P<slug>[\w_-]+)/$",
        challenge_details,
        name="challenge-details"),
    url(r"^(?P<slug>[\w_-]+)/confirm/$",
        challenge_confirm,
        name="challenge-confirm"),
    url(r"^(?P<slug>[\w_-]+)/acknowledge/$",
        challenge_acknowledge,
        name="challenge-acknowledge"),
    url(r"^(?P<slug>[\w_-]+)/edit/$",
        challenge_edit,
        name="challenge-edit"),
    url(r"^(?P<slug>[\w_-]+)/reporting-materials/$",
        challenge_reporting_materials,
        name="challenge-reporting-materials"),
]
