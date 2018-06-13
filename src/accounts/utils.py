import inspect

from django.db.models import Q

from termcolor import colored

from challenges.choices import CHALLENGE_STATUS
from challenges.models import (
    Challenge,
    Participation,
    )


# TODO: Expand django.contrib.auth.models.User and move methods there


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ HELPERS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def is_challenge_admin(user, challenge):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    admin_challenges = get_admin_challenges(user)

    if challenge in admin_challenges:
        return True

    return False


def get_admin_challenges(user):
    """Get Challenges, where User is Admin."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    orgs = user.created_organizations.all()
    admin_challenges = Challenge.objects.filter(
        Q(organization__in=orgs) |
        Q(author=user)
    )

    return admin_challenges


def get_participations_intersection(user_1, user_2):
    """Get the Queryset Intersection of two Users' Participations."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Users' Participations.
    user_participations_1 = Participation.objects.filter(
        user=user_1,
        challenge__status__in=[
            CHALLENGE_STATUS.UPCOMING,
            CHALLENGE_STATUS.COMPLETE,
        ],
    ).values_list("challenge_id", flat=True)

    print colored("[---  DUMP   ---] USER #1 : %s" % user_participations_1)

    user_participations_2 = Participation.objects.filter(
        user=user_2,
        challenge__status__in=[
            CHALLENGE_STATUS.UPCOMING,
            CHALLENGE_STATUS.COMPLETE,
        ],
    ).values_list("challenge_id", flat=True)

    print colored("[---  DUMP   ---] USER #2 : %s" % user_participations_2)

    # -------------------------------------------------------------------------
    # --- Get the Queryset Intersection.
    intersection = list(set(user_participations_1).intersection(user_participations_2))

    print colored("[---  DUMP   ---] INTXN   : %s" % intersection)

    return intersection
