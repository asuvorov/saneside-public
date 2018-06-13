from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404

from challenges.models import Challenge
from organizations.models import OrganizationStaff


def challenge_org_staff_member_required(func):
    """Restrict the Manipulations with the Challenge.

    Only for the Challenge Organization Staff Members.
    """
    def _check(request, *args, **kwargs):
        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge.
        #     Only Challenge Author, and the Organization (if set)
        #     Staff Members are allowed to modify the Challenge.
        slug = kwargs.get("slug", "")
        challenge_id = request.POST.get("challenge_id", "")

        if slug:
            challenge = get_object_or_404(
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
                slug=slug,
            )
        elif challenge_id:
            challenge = get_object_or_404(
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
        else:
            raise Http404

        # ---------------------------------------------------------------------
        # --- Return from the Decorator.
        return func(request, *args, **kwargs)

    return _check


def challenge_access_check_required(func):
    """Restrict Access to the Challenge Details."""
    def _check(request, *args, **kwargs):
        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge with the Organization Privacy Settings:
        #     1. Organization is not set;
        #     2. Organization is set to Public;
        #     3. Organization is set to Private, and:
        #        a) User is the Organization Staff Member (and/or Author);
        #        b) User is the Organization Group Member.
        # ---------------------------------------------------------------------
        slug = kwargs.get("slug", "")
        challenge_id = request.POST.get("challenge_id", "")

        if slug:
            if request.user.is_authenticated():
                challenge = get_object_or_404(
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
                            .organization_group_members
                            .all().values_list(
                                "organization_id", flat=True
                            )),
                        organization__is_hidden=True,
                    ),
                    slug=slug,
                    )
            else:
                challenge = get_object_or_404(
                    Challenge,
                    Q(organization=None) |
                    Q(organization__is_hidden=False),
                    slug=slug,
                    )
        elif challenge_id:
            if request.user.is_authenticated():
                challenge = get_object_or_404(
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
            else:
                challenge = get_object_or_404(
                    Challenge,
                    Q(organization=None) |
                    Q(organization__is_hidden=False),
                    id=challenge_id,
                    )
        else:
            raise Http404

        # ---------------------------------------------------------------------
        # --- Return from the Decorator
        return func(request, *args, **kwargs)

    return _check
