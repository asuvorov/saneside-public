from django.conf.urls import url

from accounts.pdf_export import *
from accounts.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- DESKTOP
    # -------------------------------------------------------------------------
    # --- Account List
    url(r"^$",
        account_list,
        name="account-list"),
    url(r"^near-you/$",
        account_near_you_list,
        name="account-near-you-list"),
    url(r"^might-know/$",
        account_might_know_list,
        name="account-might-know-list"),
    url(r"^new/$",
        account_new_list,
        name="account-new-list"),
    url(r"^online/$",
        account_online_list,
        name="account-online-list"),

    # -------------------------------------------------------------------------
    # --- Account Registration
    url(r"^signup/$",
        account_signup,
        name="signup"),
    url(r"^signup/confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        account_signup_confirm,
        name="signup-confirm"),
    url(r"^login/$",
        account_login,
        name="login"),
    url(r"^logout/$",
        account_logout, {
            "next_page":    "/"
        },
        name="logout"),

    # -------------------------------------------------------------------------
    # --- My Profile
    url(r"^my-profile/$",
        my_profile_view,
        name="my-profile-view"),
    url(r"^my-profile/invitations/$",
        my_profile_invitations,
        name="my-profile-invitations"),
    url(r"^my-profile/participations/$",
        my_profile_participations,
        name="my-profile-participations"),
    url(r"^my-profile/challenges/$",
        my_profile_challenges,
        name="my-profile-challenges"),

    url(r"^my-profile/edit/$",
        my_profile_edit,
        name="my-profile-edit"),
    url(r"^my-profile/delete/$",
        my_profile_delete,
        name="my-profile-delete"),
    url(r"^my-profile/privacy/$",
        my_profile_privacy,
        name="my-profile-privacy"),

    # -------------------------------------------------------------------------
    # --- Foreign Profile
    url(r"^profile/(?P<user_id>[\w_-]+)/$",
        profile_view,
        name="profile-view"),
    url(r"^profile/(?P<user_id>[\w_-]+)/participations/$",
        profile_participations,
        name="profile-participations"),
    url(r"^profile/(?P<user_id>[\w_-]+)/challenges/$",
        profile_challenges,
        name="profile-challenges"),

    # -------------------------------------------------------------------------
    # --- Freiwilligenausweis
    url(r"^my-profile/challenges/export/$",
        my_profile_challenges_export,
        name="my-profile-challenges-export"),
    url(r"^my-profile/challenges/export.pdf$",
        CompletedChallengesPDF.as_view()),

    # -------------------------------------------------------------------------
    # --- Password
    url(r"^password/renew/(?P<uidb36>[0-9A-Za-z]{1,13})-"
        "(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        password_renew,
        name="password-renew"),
    url(r"^password/reset/$",
        password_reset,
        name="password-reset"),
]
