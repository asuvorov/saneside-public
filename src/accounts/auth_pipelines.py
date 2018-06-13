import inspect
import requests

from django.core.files.base import ContentFile

import papertrail

from requests import HTTPError
from termcolor import colored

from accounts.models import (
    UserProfile,
    UserLogin,
    )


def save_profile(
        strategy, backend, uid, response, details, user, social, request,
        is_new=False, *args, **kwargs):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    print colored("[---  DUMP   ---] STRATEGY : %s" % strategy, "yellow")
    print colored("[---  DUMP   ---]  BACKEND : %s" % backend, "yellow")
    print colored("[---  DUMP   ---]      UID : %s" % uid, "yellow")
    print colored("[---  DUMP   ---] RESPONSE : %s" % response, "yellow")
    print colored("[---  DUMP   ---]  DETAILS : %s" % details, "yellow")
    print colored("[---  DUMP   ---]     USER : %s" % user, "yellow")
    print colored("[---  DUMP   ---]   SOCIAL : %s" % social, "yellow")

    avatar_url = ""

    try:
        profile = user.profile
    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")

        profile = UserProfile.objects.create(
            user=user
        )

    # -------------------------------------------------------------------------
    # --- FACEBOOK.
    # -------------------------------------------------------------------------
    if is_new and backend.name == "facebook":
        # profile.gender = response.get("gender").capitalize()
        profile.fb_profile = response.get("link")

        avatar_url =\
            "http://graph.facebook.com/{id}/picture?type=large".format(
                id=response.get("id"),)

    # -------------------------------------------------------------------------
    # --- LINKEDIN.
    # -------------------------------------------------------------------------
    if backend.name == "linkedin":
        pass

    # -------------------------------------------------------------------------
    # --- GOOGLE-PLUS.
    # -------------------------------------------------------------------------
    if backend.name == "google-oauth2":
        if response.get("image") and response["image"].get("url"):
            avatar_url = response["image"].get("url")

    # -------------------------------------------------------------------------
    # --- Import social Profile Avatar.
    # -------------------------------------------------------------------------
    if (
            avatar_url and (
                is_new or not profile.avatar)):
        try:
            response = requests.get(avatar_url)
            response.raise_for_status()
        except HTTPError:
            pass
        else:
            profile.avatar.save(
                "{username}_social.jpg".format(
                    username=user.username,
                    ),
                ContentFile(response.content))
    else:
        # ---------------------------------------------------------------------
        # --- If existing Avatar, stick with it.
        pass

    profile.save()

    # -------------------------------------------------------------------------
    # --- Track IP.
    # -------------------------------------------------------------------------
    UserLogin.objects.insert(
        request=strategy.request,
        user=user,
        provider=backend.name,
        )

    # -------------------------------------------------------------------------
    # --- Save the Log.
    papertrail.log(
        event_type="user-logged-in-social",
        message="User logged in through social Network",
        data={
            "backend":  backend.name,
            "details":  details,
            "user":     user if user else request.user.email,
            "is_new":   is_new,
        },
        # timestamp=timezone.now(),
        targets={
            "user":     user if user else request.user,
        },
        )
