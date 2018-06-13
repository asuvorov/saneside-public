from django.conf.urls import url

from organizations.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- DESKTOP
    # -------------------------------------------------------------------------
    # --- Organization List
    url(r"^$",
        organization_list,
        name="organization-list"),
    url(r"^directory/$",
        organization_directory,
        name="organization-directory"),

    # -------------------------------------------------------------------------
    # --- Organization create
    url(r"^create/$",
        organization_create,
        name="organization-create"),

    # -------------------------------------------------------------------------
    # --- Organization view/edit
    url(r"^(?P<slug>[\w_-]+)/$",
        organization_details,
        name="organization-details"),
    url(r"^(?P<slug>[\w_-]+)/staff/$",
        organization_staff,
        name="organization-staff"),
    url(r"^(?P<slug>[\w_-]+)/groups/$",
        organization_groups,
        name="organization-groups"),
    url(r"^(?P<slug>[\w_-]+)/edit/$",
        organization_edit,
        name="organization-edit"),
    url(r"^(?P<slug>[\w_-]+)/populate/$",
        organization_populate_newsletter,
        name="organization-populate-newsletter"),

    # -------------------------------------------------------------------------
    # --- iFrames
    url(r"^iframe/upcoming/(?P<organization_id>\d+)/$",
        organization_iframe_upcoming,
        name="organization-iframe-upcoming"),
    url(r"^iframe/complete/(?P<organization_id>\d+)/$",
        organization_iframe_complete,
        name="organization-iframe-complete"),
]
