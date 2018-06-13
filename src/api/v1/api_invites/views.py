import datetime
import inspect
import json

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.template import (
    Context,
    loader,
    )
from django.utils.translation import ugettext_lazy as _

from rest_framework import (
    status,
    views,
    viewsets,
    parsers,
    renderers,
    mixins
    )
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    )
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

import papertrail

from annoying.functions import get_object_or_None
from termcolor import colored

from api.auth import CsrfExemptSessionAuthentication
from challenges.choices import PARTICIPATION_STATUS
from challenges.models import (
    Challenge,
    Participation,
    )
from invites.choices import INVITE_STATUS
from invites.models import Invite
from organizations.models import (
    Organization,
    OrganizationGroup,
    OrganizationStaff,
    )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ INVITES
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class InviteListViewSet(APIView):
    """Invite List View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = InviteSerializer
    # model = Invite

    def post(self, request):
        """POST: Invite create.

            Invite to the Challenge, Organization Staff or Group with Challenge and Organization Privacy Settings.

            Receive:

                invitee_id              :uint:
                challenge_id            :uint:
                organization_id         :uint:
                org_group_id            :uint:
                invitation_text         :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "invitee_id":           1,
                    "organization_id":      100,
                    "invitation_text":      "Invitation Text"
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request.
        # ---------------------------------------------------------------------
        invitee_id = request.data.get("invitee_id", "")
        challenge_id = request.data.get("challenge_id", "")
        organization_id = request.data.get("organization_id", "")
        org_group_id = request.data.get("org_group_id", "")
        invitation_text = request.data.get("invitation_text", "")

        print colored("[---  DUMP   ---] INVITEE      ID : %s" % invitee_id, "yellow")
        print colored("[---  DUMP   ---] CHALLENGE    ID : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] ORGANIZATION ID : %s" % organization_id, "yellow")
        print colored("[---  DUMP   ---] ORG GROUP    ID : %s" % org_group_id, "yellow")
        print colored("[---  DUMP   ---] INVITATION TEXT : %s" % invitation_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors.
        # ---------------------------------------------------------------------
        if not invitee_id:
            return Response({
                "message":      _("No Invitee ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not challenge_id and not organization_id and not org_group_id:
            return Response({
                "message":      _("Neither Challenge, nor Organization, nor Organization Group ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not invitation_text:
            return Response({
                "message":      _("No Invitation Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Invitee.
        # ---------------------------------------------------------------------
        invitee = get_object_or_None(
            User,
            id=invitee_id,
        )

        if not invitee:
            return Response({
                "message":      _("Invitee not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        print colored("[---  INFO   ---] FOUND INVITEE : %s" % invitee, "cyan")

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge.
        # ---------------------------------------------------------------------
        if challenge_id:
            print colored("[---   LOG   ---] Going to retrieve the Challenge", "green")

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
                return Response({
                    "message":      _("Challenge not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            content_type = ContentType.objects.get_for_model(challenge)
            object_id = challenge.id

            print colored("[---  INFO   ---] FOUND CHALLENGE : %s" % challenge, "cyan")

        # ---------------------------------------------------------------------
        # --- Retrieve the Organization.
        # ---------------------------------------------------------------------
        if organization_id:
            print colored("[---   LOG   ---] Going to retrieve the Organization", "green")

            vals = OrganizationStaff.objects.filter(
                member=request.user,
            ).values_list("organization_id", flat=True)

            print colored("[---  DUMP   ---] %s" % vals, "yellow")

            organization = get_object_or_None(
                Organization,
                Q(author=request.user) |
                Q(pk__in=OrganizationStaff
                    .objects.filter(
                        member=request.user,
                    ).values_list(
                        "organization_id", flat=True
                    )),
                id=organization_id,
                is_deleted=False,
                )

            if not organization:
                return Response({
                    "message":      _("Organization not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            content_type = ContentType.objects.get_for_model(organization)
            object_id = organization.id

            print colored("[---  INFO   ---] FOUND ORGANIZATION : %s" % organization, "cyan")

        # ---------------------------------------------------------------------
        # --- Retrieve the Organization Group.
        # ---------------------------------------------------------------------
        if org_group_id:
            print colored("[---   LOG   ---] Going to retrieve the Org Group", "green")

            org_group = get_object_or_None(
                OrganizationGroup,
                id=org_group_id,
                organization=organization,
            )

            if not org_group:
                return Response({
                    "message":      _("Organization Group not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            content_type = ContentType.objects.get_for_model(org_group)
            object_id = org_group.id

            print colored("[---  INFO   ---] FOUND ORG GROUP : %s" % org_group, "cyan")

        # ---------------------------------------------------------------------
        # --- Create/retrieve the Invite.
        # ---------------------------------------------------------------------
        invite, created = Invite.objects.get_or_create(
            inviter=request.user,
            invitee=invitee,
            content_type=content_type,
            object_id=object_id
        )
        invite.status = INVITE_STATUS.NEW
        invite.invitation_text = invitation_text
        invite.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notifications.
        # ---------------------------------------------------------------------
        invite.email_notify_invitee_inv_created(request)
        invite.email_notify_inviter_inv_created(request)

        # ---------------------------------------------------------------------
        # --- Save the Log.
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="invite-created",
            message="Invite was created",
            data={
                "inviter":  request.user.email,
                "invitee":  invitee.email,
                "object":   invite.content_object.name,
            },
            # timestamp=timezone.now(),
            targets={
                "inviter":  request.user,
                "invitee":  invitee,
                "object":   invite.content_object,
            },
            )

        return Response({
            "message":      _("Successfully sent the Invitation."),
        }, status=status.HTTP_200_OK)

invite_list = InviteListViewSet.as_view()


class InviteArchiveViewSet(APIView):
    """Invite archive View Set."""

    authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = InviteSerializer
    # model = Invite

    def post(self, request):
        """POST: Invite archive.

            Archive all Invites, except new ones.

            Receive:

                kind                    :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "kind":             "sent",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request.
        # ---------------------------------------------------------------------
        kind = request.data.get("kind", "")

        print colored("[---  DUMP   ---] KIND : %s" % kind, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors.
        # ---------------------------------------------------------------------
        if not kind:
            return Response({
                "message":      _("No Kind provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Invitations.
        # ---------------------------------------------------------------------
        if kind == "received":
            invites = Invite.objects.filter(
                invitee=request.user,
                is_archived_for_invitee=False,
            ).exclude(
                status=INVITE_STATUS.NEW,
            )

            invites.update(
                is_archived_for_invitee=True)

        elif kind == "sent":
            invites = Invite.objects.filter(
                inviter=request.user,
                is_archived_for_inviter=False,
            ).exclude(
                status=INVITE_STATUS.NEW,
            )

            invites.update(
                is_archived_for_inviter=True)

        return Response({
            "message":      _("Successfully archived the Invitations."),
        }, status=status.HTTP_200_OK)

invite_archive_all = InviteArchiveViewSet.as_view()


class InviteAcceptViewSet(APIView):
    """Invite Accept View Set."""

    authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = InviteSerializer
    # model = Invite

    def post(self, request, invite_id):
        """POST: Invite create.

            Receive:

                invite_id               :uint:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "invite_id":        100,
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request.
        # ---------------------------------------------------------------------
        print colored("[---  DUMP   ---] INVITE ID : %s" % invite_id, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors.
        # ---------------------------------------------------------------------
        if not invite_id:
            return Response({
                "message":      _("No Invite ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Invite.
        # ---------------------------------------------------------------------
        invite = get_object_or_None(
            Invite,
            id=invite_id,
            invitee=request.user,
        )

        if not invite:
            return Response({
                "message":      _("Invite not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        if invite.status != INVITE_STATUS.NEW:
            return Response({
                "message":      _("Invite Status has been changed already."),
            }, status=status.HTTP_400_BAD_REQUEST)

        invite.status = INVITE_STATUS.ACCEPTED
        invite.date_accepted = datetime.datetime.now()
        invite.save()

        # ---------------------------------------------------------------------
        # --- Make the Invitee a Challenge Participant.
        if invite.content_type.name == "challenge":
            # -----------------------------------------------------------------
            # --- Create a Participation.
            participation, created = Participation.objects.get_or_create(
                user=invite.invitee,
                challenge=invite.content_object,
            )
            participation.application_text =\
                "Joined by Invitation from " + invite.inviter.get_full_name()
            participation.date_created = datetime.datetime.now()
            participation.status = PARTICIPATION_STATUS.CONFIRMED
            participation.date_accepted = datetime.datetime.now()
            participation.save()

        # ---------------------------------------------------------------------
        # --- Make the Invitee an Organization Staff Member.
        elif invite.content_type.name == "organization":
            org_staff_member, created =\
                OrganizationStaff.objects.get_or_create(
                    author=invite.inviter,
                    organization=invite.content_object,
                    member=invite.invitee,
                    )

            invite.content_object.subscribers.add(invite.invitee)
            invite.content_object.save()

        # ---------------------------------------------------------------------
        # --- Make the Invitee an Organization Group Member.
        elif invite.content_type.name == "organization group":
            invite.content_object.members.add(invite.invitee)
            invite.content_object.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notifications.
        # ---------------------------------------------------------------------
        invite.email_notify_invitee_inv_accepted(request)
        invite.email_notify_inviter_inv_accepted(request)

        # ---------------------------------------------------------------------
        # --- Save the Log.
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="invite-accepted",
            message="Invite was accepted",
            data={
                "inviter":  invite.inviter.email,
                "invitee":  invite.invitee.email,
                "object":   invite.content_object.name,
            },
            # timestamp=timezone.now(),
            targets={
                "inviter":  invite.inviter,
                "invitee":  invite.invitee,
                "object":   invite.content_object,
            },
            )

        return Response({
            "message":      _("Successfully accepted the Invitation."),
        }, status=status.HTTP_200_OK)

invite_accept = InviteAcceptViewSet.as_view()


class InviteRejectViewSet(APIView):
    """Invite Reject View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = InviteSerializer
    # model = Invite

    def post(self, request, invite_id):
        """POST: Invite create.

            Receive:

                invite_id               :uint:
                rejection_text          :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "rejection_text":   100,
                    "rejection_text":   "Rejection Text"
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request.
        # ---------------------------------------------------------------------
        rejection_text = request.data.get("rejection_text", "")

        print colored("[---  DUMP   ---] INVITE    ID   : %s" % invite_id, "yellow")
        print colored("[---  DUMP   ---] REJECTION TEXT : %s" % rejection_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors.
        # ---------------------------------------------------------------------
        if not invite_id:
            return Response({
                "message":      _("No Invite ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not rejection_text:
            return Response({
                "message":      _("No Rejection Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Invite.
        # ---------------------------------------------------------------------
        invite = get_object_or_None(
            Invite,
            id=invite_id,
            invitee=request.user,
        )

        if not invite:
            return Response({
                "message":      _("Invite not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        if invite.status != INVITE_STATUS.NEW:
            return Response({
                "message":      _("Invite Status has been changed already."),
            }, status=status.HTTP_400_BAD_REQUEST)

        invite.status = INVITE_STATUS.REJECTED
        invite.rejection_text = rejection_text
        invite.date_rejected = datetime.datetime.now()
        invite.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notifications.
        # ---------------------------------------------------------------------
        invite.email_notify_invitee_inv_rejected(request)
        invite.email_notify_inviter_inv_rejected(request)

        # ---------------------------------------------------------------------
        # --- Save the Log.
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="invite-rejected",
            message="Invite was rejected",
            data={
                "inviter":  invite.inviter.email,
                "invitee":  invite.invitee.email,
                "object":   invite.content_object.name,
            },
            # timestamp=timezone.now(),
            targets={
                "inviter":  invite.inviter,
                "invitee":  invite.invitee,
                "object":   invite.content_object,
            },
            )

        return Response({
            "message":      _("Successfully rejected the Invitation."),
        }, status=status.HTTP_200_OK)

invite_reject = InviteRejectViewSet.as_view()


class InviteRevokeViewSet(APIView):
    """Invite Revoke View Set."""

    authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = InviteSerializer
    # model = Invite

    def post(self, request, invite_id):
        """POST: Invite create.

            Receive:

                organization_id         :uint:
                group_name              :str:
                group_description       :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "group_name":           "Name",
                    "group_description":    "Description"
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request.
        # ---------------------------------------------------------------------
        print colored("[---  DUMP   ---] INVITE ID : %s" % invite_id, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors.
        # ---------------------------------------------------------------------
        if not invite_id:
            return Response({
                "message":      _("No Invite ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Invite.
        # ---------------------------------------------------------------------
        invite = get_object_or_None(
            Invite,
            id=invite_id,
            inviter=request.user,
        )

        if not invite:
            return Response({
                "message":      _("Invite not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        if invite.status != INVITE_STATUS.NEW:
            return Response({
                "message":      _("Invite Status has been changed already."),
            }, status=status.HTTP_400_BAD_REQUEST)

        invite.status = INVITE_STATUS.REVOKED
        invite.date_revoked = datetime.datetime.now()
        invite.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notifications.
        # ---------------------------------------------------------------------
        invite.email_notify_invitee_inv_revoked(request)
        invite.email_notify_inviter_inv_revoked(request)

        # ---------------------------------------------------------------------
        # --- Save the Log.
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="invite-revoked",
            message="Invite was revoked",
            data={
                "inviter":  invite.inviter.email,
                "invitee":  invite.invitee.email,
                "object":   invite.content_object.name,
            },
            # timestamp=timezone.now(),
            targets={
                "inviter":  invite.inviter,
                "invitee":  invite.invitee,
                "object":   invite.content_object,
            },
            )

        return Response({
            "message":      _("Successfully revoked the Invitation."),
        }, status=status.HTTP_200_OK)

invite_revoke = InviteRevokeViewSet.as_view()
