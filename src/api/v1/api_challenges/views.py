import datetime
import inspect
import json

from django.contrib.contenttypes.models import ContentType
from django.template import loader
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
from challenges.choices import (
    CHALLENGE_STATUS,
    CHALLENGE_MODE,
    PARTICIPATION_STATUS,
    RECURRENCE,
    )
from challenges.models import (
    Challenge,
    Participation,
    Role,
    )
from core.models import Rating

from .utils import (
    challenge_access_check_required,
    challenge_org_staff_member_required,
    )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ CHALLENGES
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ChallengeUpcomingViewSet(APIView):
    """Challenges upcoming View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (AllowAny, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = PostSerializer
    # model = Post

    def get(self, request):
        """GET: Challenges upcoming.

            Receive:

            Return:

                status                  200/400/404/500

            Example Payload:

                {}
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Initials.
        # ---------------------------------------------------------------------
        data = []

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        year = request.GET.get("year", "")
        month = request.GET.get("month", "")

        print colored("[---  DUMP   ---] YEAR  : %s" % year, "yellow")
        print colored("[---  DUMP   ---] MONTH : %s" % month, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not year:
            return Response({
                "message":      _("No Year provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not month:
            return Response({
                "message":      _("No Month provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Filter QuerySet by the Calendar specified Year & Month
        # ---------------------------------------------------------------------
        challenges = Challenge.objects.filter(
            status=CHALLENGE_STATUS.UPCOMING,
            start_date__gte=datetime.date.today(),
            start_date__year=year,
            start_date__month=month,
        )

        for challenge in challenges:
            data.append({
                "date":         challenge.start_date.isoformat(),
                "badge":        True,
                "name":         challenge.name,
                "body":         challenge.description,
                "footer":       challenge.address.full_address if challenge.address else "",
                "classname":    "",
            })

        return Response({
            "data":     data,
        }, status=status.HTTP_200_OK)

challenge_upcoming = ChallengeUpcomingViewSet.as_view()


class ChallengeCreateViewSet(APIView):
    """Challenge Create View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Publish draft Challenge.

            Receive:

                challenge_id            :uint:
                description_text        :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "description_text":     "Challenge Description",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        description_text = request.data.get("description_text", "")

        print colored("[---  DUMP   ---] CHALLENGE   ID   : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] DESCRIPTION TEXT : %s" % description_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("Challenge ID is not provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not description_text:
            return Response({
                "message":      _("No Description Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_org_staff_member_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        challenge.description = description_text
        challenge.status = CHALLENGE_STATUS.UPCOMING
        challenge.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------
        challenge.email_notify_admin_chl_created(request)
        challenge.email_notify_alt_person_chl_created(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="challenge-published",
            message="Challenge was published",
            data={
                "admin":        request.user.email,
                "author":       challenge.author.email,
                "name":         challenge.name,
                "status":       str(challenge.stat_status_name),
            },
            # timestamp=timezone.now(),
            targets={
                "admin":        request.user,
                "author":       challenge.author,
                "challenge":    challenge,
            },
            )

        return Response({
            "message":      _("Successfully published the Challenge."),
        }, status=status.HTTP_200_OK)

challenge_create = ChallengeCreateViewSet.as_view()


class ChallengeCompleteViewSet(APIView):
    """Challenge Complete View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Complete Challenge.

            Receive:

                challenge_id            :uint:
                description_text        :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "description_text":     "Challenge Description",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        description_text = request.data.get("description_text", "")

        print colored("[---  DUMP   ---] CHALLENGE   ID   : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] DESCRIPTION TEXT : %s" % description_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("Challenge ID is not provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not description_text:
            return Response({
                "message":      _("No Description Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_org_staff_member_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        challenge.description = description_text
        challenge.status = CHALLENGE_STATUS.COMPLETE
        challenge.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------
        Participation.email_notify_participants_chl_completed(
            request=request,
            challenge=challenge)

        challenge.email_notify_admin_chl_completed(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="challenge-completed",
            message="Challenge was completed",
            data={
                "admin":        request.user.email,
                "author":       challenge.author.email,
                "name":         challenge.name,
                "status":       str(challenge.stat_status_name),
            },
            # timestamp=timezone.now(),
            targets={
                "admin":        request.user,
                "author":       challenge.author,
                "challenge":    challenge,
            },
            )

        return Response({
            "message":      _("Successfully completed the Challenge."),
        }, status=status.HTTP_200_OK)


challenge_complete = ChallengeCompleteViewSet.as_view()


class ChallengeCloneViewSet(APIView):
    """Challenge clone View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Clone the Challenge.

            Receive:

                challenge_id            :uint:
                cloning_text            :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                     "cloning_text":         "Cloning Reason",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        cloning_text = request.data.get("cloning_text", "")

        print colored("[---  DUMP   ---] CHALLENGE ID : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] CLONING TEXT : %s" % cloning_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("Challenge ID is not provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not cloning_text:
            return Response({
                "message":      _("No Description Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_org_staff_member_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        challenge.status = CHALLENGE_STATUS.CLOSED
        challenge.closed_reason = cloning_text
        challenge.save()

        # ---------------------------------------------------------------------
        # --- Retrieve Participations
        # ---------------------------------------------------------------------
        participations = Participation.objects.filter(
            challenge=challenge,
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
                PARTICIPATION_STATUS.CONFIRMED
            ]
        )

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="challenge-cloned",
            message="Challenge was cloned",
            data={
                "admin":        request.user.email,
                "author":       challenge.author.email,
                "name":         challenge.name,
                "status":       str(challenge.stat_status_name),
            },
            # timestamp=timezone.now(),
            targets={
                "admin":        request.user,
                "author":       challenge.author,
                "challenge":    challenge,
            },
            )

        # ---------------------------------------------------------------------
        # --- Clone the Challenge
        # ---------------------------------------------------------------------
        cloned_challenge = challenge

        cloned_challenge.id = None
        cloned_challenge.pk = None
        cloned_challenge.save()

        cloned_challenge.status = CHALLENGE_STATUS.UPCOMING
        cloned_challenge.recurrence = RECURRENCE.DATELESS
        cloned_challenge.start_date = None
        cloned_challenge.start_time = None
        cloned_challenge.is_newly_created = True
        cloned_challenge.save()

        # ---------------------------------------------------------------------
        # --- Reassign Participants to the cloned Challenge
        # ---------------------------------------------------------------------
        for participation in participations:
            participation.challenge = cloned_challenge
            participation.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------
        cloned_challenge.email_notify_admin_chl_cloned(request)

        Participation.email_notify_participants_chl_cloned(
            request=request,
            challenge=cloned_challenge)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="new-challenge-created",
            message="New Challenge was created",
            data={
                "author":       cloned_challenge.author.email,
                "name":         cloned_challenge.name,
                "status":       str(cloned_challenge.stat_status_name),
            },
            # timestamp=timezone.now(),
            targets={
                "author":       cloned_challenge.author,
                "challenge":    cloned_challenge,
            },
            )

        print colored("[---  DUMP   ---] CHALLENGE PUBLIC   URL : %s" % cloned_challenge.public_url(request), "yellow")
        print colored("[---  DUMP   ---] CHALLENGE ABSOLUTE URL : %s" % cloned_challenge.get_absolute_url(), "yellow")

        return Response({
            "message":          _("Successfully cloned the Challenge."),
            "challenge_url":    cloned_challenge.get_absolute_url(),
        }, status=status.HTTP_200_OK)


challenge_clone = ChallengeCloneViewSet.as_view()


class ChallengeCloseViewSet(APIView):
    """Challenge Close View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Close the Challenge.

            Receive:

                challenge_id            :uint:
                closing_text            :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                     "closing_text":         "Closing Reason",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        closing_text = request.data.get("closing_text", "")

        print colored("[---  DUMP   ---] CHALLENGE ID : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] CLOSING TEXT : %s" % closing_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("Challenge ID is not provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not closing_text:
            return Response({
                "message":      _("No Description Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_org_staff_member_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        challenge.status = CHALLENGE_STATUS.CLOSED
        challenge.closed_reason = closing_text
        challenge.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------
        challenge.email_notify_admin_chl_closed(request)

        Participation.email_notify_participants_chl_closed(
            request=request,
            challenge=challenge)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="challenge-closed",
            message="Challenge was closed",
            data={
                "admin":        request.user.email,
                "author":       challenge.author.email,
                "name":         challenge.name,
                "status":       str(challenge.stat_status_name),
            },
            # timestamp=timezone.now(),
            targets={
                "admin":        request.user,
                "author":       challenge.author,
                "challenge":    challenge,
            },
            )

        return Response({
            "message":      _("Successfully closed the Challenge."),
        }, status=status.HTTP_200_OK)

challenge_close = ChallengeCloseViewSet.as_view()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ PARTICIPATIONS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ParticipationPostViewSet(APIView):
    """Participation post View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Sign up for the Challenge.

            Receive:

                challenge_id            :uint:
                role_id                 :uint:
                application_text        :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "role_id":              100,
                    "application_text":     "Application Text",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        role_id = request.data.get("role_id", "")
        application_text = request.data.get("application_text", "")

        print colored("[---  DUMP   ---] CHALLENGE   ID   : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] ROLE        ID   : %s" % role_id, "yellow")
        print colored("[---  DUMP   ---] APPLICATION TEXT : %s" % application_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("Challenge ID is not provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_access_check_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # --- Retrieve the Role
        # ---------------------------------------------------------------------
        role = None

        if role_id:
            role = get_object_or_None(
                Role,
                id=role_id,
            )

        # ---------------------------------------------------------------------
        # --- Create/Retrieve the Participation
        # ---------------------------------------------------------------------
        participation, created = Participation.objects.get_or_create(
            user=request.user,
            challenge=challenge,
        )
        participation.application_text = application_text
        participation.date_created = datetime.datetime.now()

        # ---------------------------------------------------------------------
        # --- IMPORTANT NOTICE
        # --- Even if the Challenge is "Free-for-all", but has the Roles
        #     specified, the Participation Status will be set to
        #     "Waiting for Confirmation".
        # --- As long as the Amount of the Participants for each Role
        #     is limited by the Challenge Admin, setting the Participation
        #     Status to "Waiting for Confirmation" (hopefully) will help
        #     to avoid uncontrolled signing up to the Challenge with Roles,
        #     and will help the Challenge Admin to pay more Attention on this
        #     Workflow.
        # ---------------------------------------------------------------------
        if role:
            participation.role = role

        # ---------------------------------------------------------------------
        # --- If the Challenge is "Free-for-All", set the Participation status
        #     to "Confirmed"
        # ---------------------------------------------------------------------
        if (
                challenge.application == CHALLENGE_MODE.FREE_FOR_ALL and
                not challenge.challenge_roles.all()):
            participation.status = PARTICIPATION_STATUS.CONFIRMED
            participation.date_accepted = datetime.datetime.now()

            # -----------------------------------------------------------------
            # --- Send Email Notification(s)
            participation.email_notify_chl_participant_confirmed(request)
            participation.email_notify_chl_admin_participant_confirmed(request)
        else:
            participation.status =\
                PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION

            # -----------------------------------------------------------------
            # --- Send Email Notification(s)
            participation.email_notify_chl_participant_waiting_conf(request)
            participation.email_notify_chl_admin_participant_waiting_conf(request)

        participation.save()

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="user-challenge-signed-up",
            message="User signed up for the Challenge",
            data={
                "user":         request.user.email,
                "challenge":    challenge.name,
                "role":         role,
            },
            # timestamp=timezone.now(),
            targets={
                "user":         request.user,
                "challenge":    challenge,
            },
            )

        return Response({
            "message":      _("Successfully posted the Participation."),
        }, status=status.HTTP_200_OK)

participation_post = ParticipationPostViewSet.as_view()


class ParticipationWithdrawViewSet(APIView):
    """Participation Withdraw View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Sign up for the Challenge.

            Receive:

                challenge_id            :uint:
                cancellation_text       :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "cancellation_text":    "Cancellation Text",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        cancellation_text = request.data.get("cancellation_text", "")

        print colored("[---  DUMP   ---] CHALLENGE    ID   : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] CANCELLATION TEXT : %s" % cancellation_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("No Challenge ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not cancellation_text:
            return Response({
                "message":      _("No Cancellation Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # --- Retrieve the Participation
        # ---------------------------------------------------------------------
        participation = get_object_or_None(
            Participation,
            user=request.user,
            challenge=challenge,
            )

        if not participation:
            return Response({
                "message":      _("Participation not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        participation.cancellation_text = cancellation_text
        participation.status = PARTICIPATION_STATUS.CANCELLED_BY_USER
        participation.date_cancelled = datetime.datetime.now()
        participation.save()

        # ---------------------------------------------------------------------
        # --- Send EMail Notification(s)
        # ---------------------------------------------------------------------
        participation.email_notify_chl_participant_withdrew(request)
        participation.email_notify_chl_admin_participant_withdrew(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="user-participation-withdrew",
            message="User withdrew the Participation",
            data={
                "user":         participation.user.email,
                "challenge":    participation.challenge.name,
            },
            # timestamp=timezone.now(),
            targets={
                "user":         participation.user,
                "challenge":    participation.challenge,
            },
            )

        return Response({
            "message":      _("Successfully withdrew the Participation."),
        }, status=status.HTTP_200_OK)

participation_withdraw = ParticipationWithdrawViewSet.as_view()


class ParticipationRemoveViewSet(APIView):
    """Participation remove View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Remove Participation.

            Receive:

                challenge_id            :uint:
                participation_id        :uint:
                cancellation_text       :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "participation_id":     100,
                    "cancellation_text":    "Cancellation Text",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        participation_id = request.data.get("participation_id", "")
        cancellation_text = request.data.get("cancellation_text", "")

        print colored("[---  DUMP   ---] CHALLENGE     ID   : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] PARTICIPATION ID   : %s" % participation_id, "yellow")
        print colored("[---  DUMP   ---] CANCELLATION  TEXT : %s" % cancellation_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("No Challenge ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not participation_id:
            return Response({
                "message":      _("No Participation ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not cancellation_text:
            return Response({
                "message":      _("No Cancellation Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_org_staff_member_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # --- Retrieve the Participation
        # ---------------------------------------------------------------------
        participation = get_object_or_None(
            Participation,
            id=participation_id,
            challenge=challenge,
        )

        if not participation:
            return Response({
                "message":      _("Participation not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        participation.status = PARTICIPATION_STATUS.CANCELLED_BY_ADMIN
        participation.cancellation_text = cancellation_text
        participation.date_cancelled = datetime.datetime.now()
        participation.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------
        participation.email_notify_chl_participant_removed(request)
        participation.email_notify_chl_admin_participant_removed(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="user-participation-removed",
            message="User was removed from the Participation",
            data={
                "admin":        request.user.email,
                "user":         participation.user.email,
                "challenge":    participation.challenge.name,
            },
            # timestamp=timezone.now(),
            targets={
                "admin":        request.user,
                "user":         participation.user,
                "challenge":    participation.challenge,
            },
            )

        return Response({
            "message":      _("Successfully removed the Participant."),
        }, status=status.HTTP_200_OK)

participation_remove = ParticipationRemoveViewSet.as_view()


class ParticipationAcceptApplicationViewSet(APIView):
    """Participation Accept Application View Set."""

    authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Accept Participation Request.

            Receive:

                challenge_id            :uint:
                participation_id        :uint:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "participation_id":     100,
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        participation_id = request.data.get("participation_id", "")

        print colored("[---  DUMP   ---] CHALLENGE     ID   : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] PARTICIPATION ID   : %s" % participation_id, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("No Challenge ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not participation_id:
            return Response({
                "message":      _("No Participation ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_org_staff_member_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # --- Retrieve the Participation
        # ---------------------------------------------------------------------
        participation = get_object_or_None(
            Participation,
            id=participation_id,
            challenge=challenge,
        )

        if not participation:
            return Response({
                "message":      _("Participation not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        participation.status = PARTICIPATION_STATUS.CONFIRMED
        participation.date_accepted = datetime.datetime.now()
        participation.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------
        participation.email_notify_chl_participant_confirmed(request)
        participation.email_notify_chl_admin_participant_confirmed(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="user-participation-accepted",
            message="User was accepted for the Participation",
            data={
                "admin":        request.user.email,
                "user":         participation.user.email,
                "challenge":    participation.challenge.name,
            },
            # timestamp=timezone.now(),
            targets={
                "admin":        request.user,
                "user":         participation.user,
                "challenge":    participation.challenge,
            },
            )

        # ---------------------------------------------------------------------
        # --- Render the Participant's Thumbnail
        # ---------------------------------------------------------------------
        template = loader.get_template("challenges/fragments/challenge-participant-thumbnail.html")
        context = {
            "account":          participation.user,
            "challenge":        challenge,
            "participation":    participation,
            "is_admin":         True,
            "request":          request,
        }
        rendered = template.render(context)

        return Response({
            "message":      _("Successfully accepted the Participation Request."),
            "participant":  rendered,
        }, status=status.HTTP_200_OK)

participation_accept_application = ParticipationAcceptApplicationViewSet.as_view()


class ParticipationRejectApplicationViewSet(APIView):
    """Participation reject Application View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Reject Participation Request.

            Receive:

                challenge_id            :uint:
                participation_id        :uint:
                cancellation_text       :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "participation_id":     100,
                    "cancellation_text":    "Cancellation Text",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        participation_id = request.data.get("participation_id", "")
        cancellation_text = request.data.get("cancellation_text", "")

        print colored("[---  DUMP   ---] CHALLENGE     ID   : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] PARTICIPATION ID   : %s" % participation_id, "yellow")
        print colored("[---  DUMP   ---] CANCELLATION  TEXT : %s" % cancellation_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("No Challenge ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not participation_id:
            return Response({
                "message":      _("No Participation ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not cancellation_text:
            return Response({
                "message":      _("No Cancellation Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_org_staff_member_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # --- Retrieve the Participation
        # ---------------------------------------------------------------------
        participation = get_object_or_None(
            Participation,
            id=participation_id,
            challenge=challenge,
        )

        if not participation:
            return Response({
                "message":      _("Participation not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        participation.status = PARTICIPATION_STATUS.CONFIRMATION_DENIED
        participation.cancellation_text = cancellation_text
        participation.date_cancelled = datetime.datetime.now()
        participation.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------
        participation.email_notify_chl_participant_rejected(request)
        participation.email_notify_chl_admin_participant_rejected(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="user-participation-rejected",
            message="User was rejected from the Participation",
            data={
                "admin":        request.user.email,
                "user":         participation.user.email,
                "challenge":    participation.challenge.name,
            },
            # timestamp=timezone.now(),
            targets={
                "admin":        request.user,
                "user":         participation.user,
                "challenge":    participation.challenge,
            },
            )

        return Response({
            "message":      _("Successfully rejected the Participation Request."),
        }, status=status.HTTP_200_OK)

participation_reject_application = ParticipationRejectApplicationViewSet.as_view()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ EXPERIENCE REPORTS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SelfreflectionSubmitViewSet(APIView):
    """Self-reflection submit View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Submit Experience Report (Self-reflection).

            Receive:

                challenge_id                    :uint:
                selfreflection_activity_text    :str:
                selfreflection_learning_text    :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "selfreflection_activity_text":     "Self-reflection Activity Text"
                    "selfreflection_learning_text":     "Self-reflection learning Text",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        selfreflection_activity_text = request.data.get("selfreflection_activity_text", "")
        selfreflection_learning_text = request.data.get("selfreflection_learning_text", "")

        print colored("[---  DUMP   ---] CHALLENGE   ID   : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] SR ACTIVITY TEXT : %s" % selfreflection_activity_text, "yellow")
        print colored("[---  DUMP   ---] SR LEARNING TEXT : %s" % selfreflection_learning_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("No Challenge ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not selfreflection_activity_text:
            return Response({
                "message":      _("No Activity Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not selfreflection_learning_text:
            return Response({
                "message":      _("No Learning Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # --- Retrieve the Participation
        # ---------------------------------------------------------------------
        participation = get_object_or_None(
            Participation,
            user=request.user,
            challenge=challenge,
        )

        if not participation:
            return Response({
                "message":      _("Participation not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        participation.selfreflection_activity_text =\
            selfreflection_activity_text
        participation.selfreflection_learning_text =\
            selfreflection_learning_text

        if challenge.accept_automatically:
            # -----------------------------------------------------------------
            # --- Automatically accept Experience Reports
            participation.status = PARTICIPATION_STATUS.ACKNOWLEDGED
            participation.acknowledgement_text = challenge.acceptance_text
            participation.date_acknowledged = datetime.datetime.now()
            participation.save()

            # -----------------------------------------------------------------
            # --- Send Email Notification(s)
            participation.email_notify_chl_participant_sr_accepted(request)

        else:
            participation.status =\
                PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT
            participation.date_selfreflection = datetime.datetime.now()
            participation.save()

            # -----------------------------------------------------------------
            # --- Send Email Notification(s)
            participation.email_notify_chl_participant_sr_submitted(request)
            participation.email_notify_chl_admin_participant_sr_submitted(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="user-experience-report-submitted",
            message="User submitted the Experience Report",
            data={
                "user":         participation.user.email,
                "challenge":    participation.challenge.name,
            },
            # timestamp=timezone.now(),
            targets={
                "user":         participation.user,
                "challenge":    participation.challenge,
            },
            )

        return Response({
            "message":      _("Successfully submitted the Experience Report."),
        }, status=status.HTTP_200_OK)

challenge_selfreflection_submit = SelfreflectionSubmitViewSet.as_view()


class SelfreflectionAcceptViewSet(APIView):
    """Self-reflection accept View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Accept Experience Report (Self-reflection).

            Receive:

                challenge_id            :uint:
                participation_id        :uint:
                acknowledgement_text    :str:
                participant_rating      :int:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "participation_id":         100,
                    "acknowledgement_text":     "Acknowledgment Text",
                    "participant_rating":       5,
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        participation_id = request.data.get("participation_id", "")
        acknowledgement_text = request.data.get("acknowledgement_text", "")
        participant_rating = request.data.get("participant_rating", "")

        print colored("[---  DUMP   ---] CHALLENGE          ID     : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] PARTICIPATION      ID     : %s" % participation_id, "yellow")
        print colored("[---  DUMP   ---] SR ACKNOWLEDGEMENT TEXT   : %s" % acknowledgement_text, "yellow")
        print colored("[---  DUMP   ---] PARTICIPANT        RATING : %s" % participant_rating, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("No Challenge ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not participation_id:
            return Response({
                "message":      _("No Participation ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not acknowledgement_text:
            return Response({
                "message":      _("No Acknowledgment Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_org_staff_member_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # --- Retrieve the Participation
        # ---------------------------------------------------------------------
        participation = get_object_or_None(
            Participation,
            id=participation_id,
            challenge=challenge,
        )

        if not participation:
            return Response({
                "message":      _("Participation not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        participation.status = PARTICIPATION_STATUS.ACKNOWLEDGED
        participation.acknowledgement_text = acknowledgement_text
        participation.date_acknowledged = datetime.datetime.now()
        participation.save()

        # ---------------------------------------------------------------------
        # --- Rate the Participant
        # ---------------------------------------------------------------------
        if participant_rating:
            content_type = ContentType.objects.get_for_model(
                participation.user.profile)
            object_id = participation.user.profile.id

            rating, created = Rating.objects.get_or_create(
                author=request.user,
                content_type=content_type,
                object_id=object_id,
            )
            rating.rating = int(participant_rating)
            rating.review_text = acknowledgement_text
            rating.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------
        participation.email_notify_chl_participant_sr_accepted(request)
        participation.email_notify_chl_admin_participant_sr_accepted(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="user-experience-report-accepted",
            message="User's Experience Report was accepted",
            data={
                "admin":        request.user.email,
                "user":         participation.user.email,
                "challenge":    participation.challenge.name,
            },
            # timestamp=timezone.now(),
            targets={
                "admin":        request.user,
                "user":         participation.user,
                "challenge":    participation.challenge,
            },
            )

        return Response({
            "message":      _("Successfully accepted the Experience Report."),
        }, status=status.HTTP_200_OK)

participation_accept_selfreflection = SelfreflectionAcceptViewSet.as_view()


class SelfreflectionRejectViewSet(APIView):
    """Self-reflection reject View Set."""

    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ChallengeSerializer
    # model = Challenge

    def post(self, request, challenge_id):
        """POST: Reject Experience Report (Self-reflection).

            Receive:

                challenge_id                    :uint:
                participation_id                :uint:
                selfreflection_rejection_text   :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "participation_id":                 100,
                    "selfreflection_rejection_text":    "Self-reflection Rejection Text",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        participation_id = request.data.get("participation_id", "")
        selfreflection_rejection_text = request.data.get("selfreflection_rejection_text", "")

        print colored("[---  DUMP   ---] CHALLENGE     ID   : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] PARTICIPATION ID   : %s" % participation_id, "yellow")
        print colored("[---  DUMP   ---] SR REJECTION  TEXT : %s" % selfreflection_rejection_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id:
            return Response({
                "message":      _("No Challenge ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not participation_id:
            return Response({
                "message":      _("No Participation ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not selfreflection_rejection_text:
            return Response({
                "message":      _("No Rejection Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Check the Rights
        # ---------------------------------------------------------------------
        if not challenge_org_staff_member_required(request, challenge_id):
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        challenge = get_object_or_None(
            Challenge,
            id=challenge_id,
        )

        if not challenge:
            return Response({
                "message":      _("Challenge not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # --- Retrieve the Participation
        # ---------------------------------------------------------------------
        participation = get_object_or_None(
            Participation,
            id=participation_id,
            challenge=challenge,
        )

        if not participation:
            return Response({
                "message":      _("Participation not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        participation.status = PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION
        participation.selfreflection_rejection_text =\
            selfreflection_rejection_text
        participation.date_selfreflection_rejection = datetime.datetime.now()
        participation.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------
        participation.email_notify_chl_participant_sr_rejected(request)
        participation.email_notify_chl_admin_participant_sr_rejected(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="user-experience-report-rejected",
            message="User's Experience Report was rejected",
            data={
                "admin":        request.user.email,
                "user":         participation.user.email,
                "challenge":    participation.challenge.name,
            },
            # timestamp=timezone.now(),
            targets={
                "admin":        request.user,
                "user":         participation.user,
                "challenge":    participation.challenge,
            },
            )

        return Response({
            "message":      _("Successfully rejected the Experience Report."),
        }, status=status.HTTP_200_OK)

participation_reject_selfreflection = SelfreflectionRejectViewSet.as_view()
