from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404

from organizations.models import (
    Organization,
    OrganizationStaff,
    )


def organization_staff_member_required(func):
    """Restrict the Manipulations with the Organization.

    Only for the Organization Staff Members.
    """
    def _check(request, *args, **kwargs):
        # ---------------------------------------------------------------------
        # --- Retrieve the Organization.
        slug = kwargs.get("slug", "")
        organization_id = request.POST.get("organization_id", "")

        if slug:
            organization = get_object_or_404(
                Organization,
                Q(pk__in=OrganizationStaff
                    .objects.filter(
                        member=request.user,
                    ).values_list(
                        "organization_id", flat=True
                    )),
                slug=slug,
                is_deleted=False,
                )
        elif organization_id:
            organization = get_object_or_404(
                Organization,
                Q(pk__in=OrganizationStaff
                    .objects.filter(
                        member=request.user,
                    ).values_list(
                        "organization_id", flat=True
                    )),
                id=organization_id,
                is_deleted=False,
                )
        else:
            raise Http404

        # ---------------------------------------------------------------------
        # --- Return from the Decorator.
        return func(request, *args, **kwargs)

    return _check


def organization_access_check_required(func):
    """Restrict Access to the Organization Details.

    Only for the Organization Staff and Group Members.
    """
    def _check(request, *args, **kwargs):
        # ---------------------------------------------------------------------
        # --- Retrieve the Organization.
        slug = kwargs.get("slug", "")
        organization_id = request.POST.get("organization_id", "")

        if slug:
            if request.user.is_authenticated():
                organization = get_object_or_404(
                    Organization,
                    Q(is_hidden=False) |
                    Q(
                        Q(pk__in=OrganizationStaff.objects.filter(
                                member=request.user,
                            ).values_list(
                                "organization_id", flat=True
                            )) |
                        Q(pk__in=request.user
                            .organization_group_members
                            .all().values_list(
                                "organization_id", flat=True
                            )),
                        is_hidden=True,
                    ),
                    slug=slug,
                    is_deleted=False,
                    )
            else:
                organization = get_object_or_404(
                    Organization,
                    slug=slug,
                    is_hidden=False,
                    is_deleted=False,
                    )
        elif organization_id:
            if request.user.is_authenticated():
                organization = get_object_or_404(
                    Organization,
                    Q(is_hidden=False) |
                    Q(
                        Q(pk__in=OrganizationStaff
                            .objects.filter(
                                member=request.user,
                            ).values_list(
                                "organization_id", flat=True
                            )) |
                        Q(pk__in=request.user
                            .organization_group_members
                            .all().values_list(
                                "organization_id", flat=True
                            )),
                        is_hidden=True,
                    ),
                    id=organization_id,
                    is_deleted=False,
                    )
            else:
                organization = get_object_or_404(
                    Organization,
                    id=organization_id,
                    is_hidden=False,
                    is_deleted=False,
                    )
        else:
            raise Http404

        # ---------------------------------------------------------------------
        # --- Return from the Decorator.
        return func(request, *args, **kwargs)

    return _check
