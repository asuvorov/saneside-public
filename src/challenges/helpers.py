from django.db.models import Q

from challenges.filters import ChallengeFilter
from challenges.models import Challenge
from organizations.models import OrganizationStaff


def get_challenge_list(request):
    """Return the List of the Challenges."""
    # -------------------------------------------------------------------------
    # --- Retrieve the Challenges with the Organization Privacy Settings:
    #     1. Organization is not set;
    #     2. Organization is set to Public;
    #     3. Organization is set to Private, and:
    #        a) User is the Organization Staff Member (and/or Author);
    #        b) User is the Organization Group Member.
    # -------------------------------------------------------------------------
    if request.user.is_authenticated():
        challenges = Challenge.objects.filter(
            Q(organization=None) |
            Q(organization__is_hidden=False) |
            Q(
                Q(organization__pk__in=OrganizationStaff
                    .objects.filter(
                        member=request.user,
                    ).values_list(
                        "organization_id", flat=True
                    )) |
                Q(organization__pk__in=request.user
                    .organization_group_members
                    .all().values_list(
                        "organization_id", flat=True
                    )),
                organization__is_hidden=True,
            ),
        )
    else:
        challenges = Challenge.objects.filter(
            Q(organization=None) |
            Q(organization__is_hidden=False),
        )

    print ">>> HELPERS > CHALLENGES : ", challenges.count()

    challenge_filter = ChallengeFilter(
        request.GET,
        queryset=challenges)

    return challenge_filter.qs
