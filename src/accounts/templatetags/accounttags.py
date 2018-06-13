from django import template
from django.db.models import Sum, Q

from termcolor import colored

from accounts.choices import (
    WHO_CAN_SEE_MEMBERS,
    WHO_CAN_SEE_ADMINS,
    )
from challenges.choices import (
    CHALLENGE_STATUS,
    PARTICIPATION_STATUS,
    )
from challenges.models import (
    Challenge,
    Participation,
    )
from organizations.models import (
    Organization,
    OrganizationStaff,
    )


register = template.Library()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ PRIVACY
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def check_privacy(request, account, flag_members, flag_admins):
    """Docstring."""
    # -------------------------------------------------------------------------
    # --- Initials.
    # -------------------------------------------------------------------------
    result = False

    # -------------------------------------------------------------------------
    # --- Platform Admins.
    # -------------------------------------------------------------------------
    if request.user.is_authenticated() and request.user.is_staff:
        return True

    # -------------------------------------------------------------------------
    # --- Check the Privacy Members.
    # -------------------------------------------------------------------------
    if (
            flag_members == WHO_CAN_SEE_MEMBERS.NO_ONE):
        # --- No-one.

        # --- Proceed to the Challenge Admins (Organizers) Privacy.
        result = False
    elif (
            flag_members == WHO_CAN_SEE_MEMBERS.REGISTERED and
            request.user.is_authenticated()):
        # --- Registered Users only.

        # --- Return True.
        #     It also covers the Challenge Organizers Privacy, because only
        #     the registered Users can create the Challenges.
        return True
    elif (
            flag_members == WHO_CAN_SEE_MEMBERS.CHL_MEMBERS and
            request.user.is_authenticated()):
        # --- Participants of the Challenges, the User participate in as well.
        challenge_ids = account.user_participations.confirmed().values_list(
            "challenge_id", flat=True)

        participations = Participation.objects.filter(
            user=request.user,
            challenge__pk__in=challenge_ids,
        )

        if participations.exists():
            # --- Return True.
            return True

        # --- Proceed to the Challenge Organizers Privacy.
        result = False
    elif (
            flag_members == WHO_CAN_SEE_MEMBERS.ORG_MEMBERS and
            request.user.is_authenticated()):
        # --- Staff/Group Members of the Organization(s), the User
        #     affiliated with.

        # --- Retrieve the List of the Organizations' IDs, where the Account is
        #     either Author, or Staff Member, or Group Member.
        account_organization_ids = Organization.objects.filter(
            Q(author=account) |
            Q(pk__in=OrganizationStaff
                .objects.filter(
                    member=account,
                ).values_list(
                    "organization_id", flat=True
                )) |
            Q(pk__in=account
                .organization_group_members
                .all().values_list(
                    "organization_id", flat=True
                )),
            is_deleted=False,
        ).values_list(
            "id", flat=True
        )

        print colored("[---  DUMP   ---] ACCOUNT ORGANIZATION ID : %s" % account_organization_ids, "yellow")

        # --- Retrieve the List of the Organizations' IDs,
        #     where the Request User is either Author, or Staff Member,
        #     or Group Member, and this List overlaps
        #     `account_organization_ids` List.
        request_user_organization_ids = Organization.objects.filter(
            Q(author=request.user) |
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
            pk__in=account_organization_ids,
            is_deleted=False,
        ).values_list(
            "id", flat=True
        )

        print colored("[---  DUMP   ---] REQUEST USER ORGANIZATION ID : %s" % request_user_organization_ids, "yellow")

        if request_user_organization_ids:
            # --- Return True.
            return True

        # --- Proceed to the Challenge Organizers Privacy.
        result = False
    elif (
            flag_members == WHO_CAN_SEE_MEMBERS.EVERYONE):
        # --- Everyone.

        # --- Return True.
        #     It also covers the Challenge Admins (Organizers) Privacy.
        return True

    # -------------------------------------------------------------------------
    # --- Check the Privacy Admins (Organizers)
    # -------------------------------------------------------------------------
    if (
            flag_admins == WHO_CAN_SEE_ADMINS.NO_ONE):
        # --- No-one
        result = False
    elif (
            flag_admins == WHO_CAN_SEE_ADMINS.PARTICIPATED and
            request.user.is_authenticated()):
        # --- Admins of the Challenges, I participate(-d) in.
        challenge_ids = account.user_participations.confirmed().values_list(
            "challenge_id", flat=True)
        challenges = Challenge.objects.filter(
            pk__in=challenge_ids,
            author=request.user,
            )

        if challenges.exists():
            # --- Return True.
            return True

        result = False
    elif (
            flag_admins == WHO_CAN_SEE_ADMINS.ALL and
            request.user.is_authenticated()):
        # --- Admins of the upcoming Challenges on the Platform.
        challenges = Challenge.objects.filter(
            author=request.user,
            status=CHALLENGE_STATUS.UPCOMING,
            )

        if challenges.exists():
            # --- Return True.
            return True

        result = False

    # -------------------------------------------------------------------------
    # --- Return.
    return result


@register.assignment_tag
def need_to_know_profile_details_tag(request, account):
    """Who can see the Profile Details.

    (e.g. Avatar, Name, Bio, Gender, Birthday).
    """
    return check_privacy(
        request=request,
        account=account,
        flag_members=account.privacy_members.profile_details,
        flag_admins=account.privacy_admins.profile_details)


@register.assignment_tag
def need_to_know_contact_details_tag(request, account):
    """Who can see the Contact Details (e.g. Address, Phone #, Email)."""
    return check_privacy(
        request=request,
        account=account,
        flag_members=account.privacy_members.contact_details,
        flag_admins=account.privacy_admins.contact_details)


@register.assignment_tag
def need_to_know_upcoming_challenges_tag(request, account):
    """Who can see the List of upcoming Challenges."""
    return check_privacy(
        request=request,
        account=account,
        flag_members=account.privacy_members.challenges_upcoming,
        flag_admins=account.privacy_admins.challenges_upcoming)


@register.assignment_tag
def need_to_know_completed_challenges_tag(request, account):
    """Who can see the List completed Challenges."""
    return check_privacy(
        request=request,
        account=account,
        flag_members=account.privacy_members.challenges_completed,
        flag_admins=account.privacy_admins.challenges_completed)


@register.assignment_tag
def need_to_know_affiliated_challenges_tag(request, account):
    """Who can see the List of affiliated Challenges."""
    return check_privacy(
        request=request,
        account=account,
        flag_members=account.privacy_members.challenges_affiliated,
        flag_admins=account.privacy_admins.challenges_affiliated)


@register.assignment_tag
def need_to_know_canceled_participations_tag(request, account):
    """Who can see the List of canceled (withdrawn) Participations."""
    return check_privacy(
        request=request,
        account=account,
        flag_members=account.privacy_members.participations_canceled,
        flag_admins=account.privacy_admins.participations_canceled)


@register.assignment_tag
def need_to_know_rejected_participations_tag(request, account):
    """Who can see the List of rejected Participations."""
    return check_privacy(
        request=request,
        account=account,
        flag_members=account.privacy_members.participations_rejected,
        flag_admins=account.privacy_admins.participations_rejected)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ DIFFERENT
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@register.assignment_tag
def sum_of_hours_spent_tag(account):
    """Docstring."""
    sum_of_hours_spent = Challenge.objects.filter(
        pk__in=Participation.objects.filter(
            user=account,
            status=PARTICIPATION_STATUS.ACKNOWLEDGED
        ).values_list("challenge_id", flat=True)
    ).aggregate(Sum("duration"))

    if sum_of_hours_spent["duration__sum"]:
        return sum_of_hours_spent["duration__sum"]
    else:
        return 0


@register.assignment_tag
def is_rated_challenge_tag(challenge, account):
    """Docstring."""
    return challenge.is_rated_by_user(account)


@register.assignment_tag
def is_complained_challenge_tag(challenge, account):
    """Docstring."""
    return challenge.is_complained_by_user(account)
