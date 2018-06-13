from django.conf.urls import include, url

from .views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Organizations
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # --- Admin actions

    # --- Staff Members Order
    url(r"^(?P<organization_id>[\w_-]+)/staff-member/order/$",
        staff_member_order,
        name="api-organization-staff-member-order"),

    # --- Staff Members edit/remove
    url(r"^(?P<organization_id>[\w_-]+)/staff-member/edit/$",
        staff_member_edit,
        name="api-organization-staff-member-edit"),
    url(r"^(?P<organization_id>[\w_-]+)/staff-member/remove/$",
        staff_member_remove,
        name="api-organization-staff-member-remove"),

    # --- Groups
    url(r"^(?P<organization_id>[\w_-]+)/groups/$",
        group_list,
        name="api-organization-group-list"),
    url(r"^(?P<organization_id>[\w_-]+)/groups/remove/$",
        group_remove,
        name="api-organization-group-remove"),

    # --- Group Members
    url(r"^(?P<organization_id>[\w_-]+)/group-member/remove/$",
        group_member_remove,
        name="api-organization-group-member-remove"),

    # -------------------------------------------------------------------------
    # --- User actions
    url(r"^(?P<organization_id>[\w_-]+)/subscribe/$",
        subscribe,
        name="api-organization-subscribe"),
]
