import inspect

from django.db.models import Q

from annoying.functions import get_object_or_None
from termcolor import colored

from challenges.models import Challenge
from organizations.models import OrganizationStaff


def challenge_access_check_required(request, challenge_id):
    """Restrict Access to the Challenge Details."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve the Challenge with the Organization Privacy Settings:
    #     1. Organization is not set;
    #     2. Organization is set to Public;
    #     3. Organization is set to Private, and:
    #        a) User is the Organization Staff Member (and/or Author);
    #        b) User is the Organization Group Member.
    # -------------------------------------------------------------------------
    challenge = get_object_or_None(
        Challenge,
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
                .organization_group_members.all().values_list(
                    "organization_id", flat=True
                )),
            organization__is_hidden=True,
        ),
        id=challenge_id,
        )

    if not challenge:
        return False

    return True


def challenge_org_staff_member_required(request, challenge_id):
    """Restrict the Manipulations with the Challenge.

    Only for the Challenge Organization Staff Members.
    """
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve the Challenge.
    #     Only Challenge Author, and the Organization (if set)
    #     Staff Members are allowed to modify the Challenge.
    challenge = get_object_or_None(
        Challenge,
        Q(
            Q(organization=None) &
            Q(author=request.user),
        ) |
        Q(
            Q(organization__pk__in=OrganizationStaff
                .objects.filter(
                    member=request.user,
                ).values_list(
                    "organization_id", flat=True
                )),
        ),
        id=challenge_id,
        )

    if not challenge:
        return False

    return True
