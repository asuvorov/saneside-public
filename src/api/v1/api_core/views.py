import datetime
import inspect
import json

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
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

from accounts.models import UserProfile
from accounts.utils import get_participations_intersection
from api.auth import CsrfExemptSessionAuthentication
from api.v1.api_challenges.utils import (
    challenge_access_check_required,
    challenge_org_staff_member_required,
    )
from api.v1.api_organizations.utils import (
    organization_access_check_required,
    organization_staff_member_required,
    )
from blog.models import Post
from challenges.choices import (
    CHALLENGE_STATUS,
    PARTICIPATION_STATUS,
    )
from challenges.models import (
    Challenge,
    Participation,
    )
from core.models import (
    Comment,
    Complaint,
    Rating,
    )
from organizations.models import (
    Organization,
    OrganizationStaff,
    )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ COMMENTS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CommentListViewSet(APIView):
    """Comment List View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = CommentSerializer
    # model = Comment

    def post(self, request):
        """POST: Comment create.

            Receive:

                challenge_id            :uint:
                organization_id         :uint:
                post_id                 :uint:
                comment_text            :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "challenge_id":         1,
                    "comment_text":         "Comment Text"
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        challenge_id = request.data.get("challenge_id", "")
        organization_id = request.data.get("organization_id", "")
        post_id = request.data.get("post_id", "")
        comment_text = request.data.get("comment_text", "")

        print colored("[---  DUMP   ---] CHALLENGE    ID : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] ORGANIZATION ID : %s" % organization_id, "yellow")
        print colored("[---  DUMP   ---] POST         ID : %s" % post_id, "yellow")
        print colored("[---  DUMP   ---] COMMENT    TEXT : %s" % comment_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id and not organization_id and not post_id:
            return Response({
                "message":      _("Neither Challenge, nor Organization, nor Post ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not comment_text:
            return Response({
                "message":      _("No Comment Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        if challenge_id:
            print colored("[---   LOG   ---] Going to retrieve the Challenge", "green")

            # -----------------------------------------------------------------
            # --- Check the Rights
            # -----------------------------------------------------------------
            if not challenge_access_check_required(request, challenge_id):
                return Response({
                    "message":      _("You don't have Permissions to perform the Action."),
                }, status=status.HTTP_400_BAD_REQUEST)

            # -----------------------------------------------------------------
            # --- Retrieve the Challenge
            # -----------------------------------------------------------------
            challenge = get_object_or_None(
                Challenge,
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
        # --- Retrieve the Organization
        # ---------------------------------------------------------------------
        if organization_id:
            print colored("[---   LOG   ---] Going to retrieve the Organization", "green")

            # -----------------------------------------------------------------
            # --- Check the Rights
            # -----------------------------------------------------------------
            if not organization_access_check_required(request, organization_id):
                return Response({
                    "message":      _("You don't have Permissions to perform the Action."),
                }, status=status.HTTP_400_BAD_REQUEST)

            # -----------------------------------------------------------------
            # --- Retrieve the Organization
            # -----------------------------------------------------------------
            organization = get_object_or_None(
                Organization,
                id=organization_id,
            )

            if not organization:
                return Response({
                    "message":      _("Organization not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            content_type = ContentType.objects.get_for_model(organization)
            object_id = organization.id

            print colored("[---  INFO   ---] FOUND ORGANIZATION : %s" % organization, "cyan")

        # ---------------------------------------------------------------------
        # --- Retrieve the Post
        # ---------------------------------------------------------------------
        if post_id:
            print colored("[---   LOG   ---] Going to retrieve the Blog Post", "green")

            post = get_object_or_None(
                Post,
                id=post_id,
            )

            if not post:
                return Response({
                    "message":      _("Blog Post not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            content_type = ContentType.objects.get_for_model(post)
            object_id = post.id

            print colored("[---  INFO   ---] FOUND BLOG POST : %s" % post, "cyan")

        # ---------------------------------------------------------------------
        # --- Create Comment
        # ---------------------------------------------------------------------
        comment = Comment.objects.create(
            user=request.user,
            text=comment_text,
            content_type=content_type,
            object_id=object_id,
        )
        comment.save()

        template = loader.get_template("common/fragments/comment-hor.html")
        context = {
            "comment":  comment,
            "request":  request,
        }
        rendered = template.render(context)

        return Response({
            "message":      _("Successfully added the Comment."),
            "comment":      rendered,
        }, status=status.HTTP_200_OK)

comment_list = CommentListViewSet.as_view()


class CommentDetailsViewSet(APIView):
    """Comment Details View Set."""

    authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = CommentSerializer
    # model = Comment

    def delete(self, request, comment_id):
        """DELETE: Comment delete.

            Receive:

                comment_id              :uint:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "comment_id":       100,
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        print colored("[---  DUMP   ---] COMMENT ID : %s" % comment_id, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not comment_id:
            return Response({
                "message":      _("No Comment ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Comment
        # ---------------------------------------------------------------------
        comment = get_object_or_None(
            Comment,
            pk=comment_id,
        )

        if not comment:
            return Response({
                "message":      _("Comment not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        if request.user != comment.user and not request.user.is_staff:
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        comment.is_deleted = True
        comment.save()

        return Response({
            "message":      _("Successfully removed the Comment."),
        }, status=status.HTTP_200_OK)

comment_details = CommentDetailsViewSet.as_view()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ COMPLAINTS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ComplaintListViewSet(APIView):
    """Complaint List View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = ComplaintSerializer
    # model = Complaint

    def post(self, request):
        """POST: Complaint create.

            Receive:

                account_id              :uint:
                challenge_id            :uint:
                organization_id         :uint:
                post_id                 :uint:

                complaint_text          :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "challenge_id":         1,
                    "complaint_text":       "Complaint Text"
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        account_id = request.data.get("account_id", "")
        challenge_id = request.data.get("challenge_id", "")
        organization_id = request.data.get("organization_id", "")
        complaint_text = request.data.get("complaint_text", "")

        print colored("[---  DUMP   ---] ACCOUNT      ID : %s" % account_id, "yellow")
        print colored("[---  DUMP   ---] CHALLENGE    ID : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] ORGANIZATION ID : %s" % organization_id, "yellow")
        print colored("[---  DUMP   ---] COMPLAINT  TEXT : %s" % complaint_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not account_id and not challenge_id and not organization_id:
            return Response({
                "message":      _("Neither Account, nor Challenge, nor Organization, ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not complaint_text:
            return Response({
                "message":      _("No Complaint Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Account
        # ---------------------------------------------------------------------
        if account_id:
            account = get_object_or_None(
                User,
                id=account_id,
            )

            if not account:
                return Response({
                    "message":      _("Member not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            # -----------------------------------------------------------------
            # --- Check, if the User has already complained to the Account
            is_complained = account.profile.is_complained_by_user(
                request.user)

            if is_complained:
                return Response({
                    "message":      _("You already complained on the Member."),
                }, status=status.HTTP_400_BAD_REQUEST)

            # -----------------------------------------------------------------
            # --- Check, if the registered User participated in the same
            #     Challenge(s), as the Account.
            if len(get_participations_intersection(request.user, account)) <= 0:
                return Response({
                    "message":      _("You don't have Permissions to perform the Action."),
                }, status=status.HTTP_400_BAD_REQUEST)

            content_type = ContentType.objects.get_for_model(account.profile)
            object_id = account.profile.id

        # ---------------------------------------------------------------------
        # --- Retrieve the Challenge
        # ---------------------------------------------------------------------
        if challenge_id:
            challenge = get_object_or_None(
                Challenge,
                id=challenge_id,
            )

            if not challenge:
                return Response({
                    "message":      _("Challenge not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            # -----------------------------------------------------------------
            # --- Check, if the User has already complained to the Account
            is_complained = challenge.is_complained_by_user(
                request.user)

            if is_complained:
                return Response({
                    "message":      _("You already complained on the Challenge."),
                }, status=status.HTTP_400_BAD_REQUEST)

            # -----------------------------------------------------------------
            # --- Check, if the registered User participated in the Challenge.
            participation = get_object_or_None(
                Participation,
                user=request.user,
                challenge=challenge,
            )

            if not participation:
                return Response({
                    "message":      _("You don't have Permissions to perform the Action."),
                }, status=status.HTTP_400_BAD_REQUEST)

            if (
                    not participation.is_waiting_for_selfreflection and
                    not participation.is_waiting_for_acknowledgement and
                    not participation.is_acknowledged):
                return Response({
                    "message":      _("You don't have Permissions to perform the Action."),
                }, status=status.HTTP_400_BAD_REQUEST)

            content_type = ContentType.objects.get_for_model(challenge)
            object_id = challenge.id

        # ---------------------------------------------------------------------
        # --- Retrieve the Organization
        # ---------------------------------------------------------------------
        if organization_id:
            organization = get_object_or_None(
                Organization,
                id=organization_id,
            )

            if not organization:
                return Response({
                    "message":      _("Organization not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            # -----------------------------------------------------------------
            # --- Check, if the User has already complained to the Organization.
            is_complained = organization.is_complained_by_user(
                request.user)

            if is_complained:
                return Response({
                    "message":      _("You already complained on the Organization."),
                }, status=status.HTTP_400_BAD_REQUEST)

            # -----------------------------------------------------------------
            # --- Retrieve User's Participations to the Organization's
            #     Challenges.
            completed_challenges = Challenge.objects.filter(
                organization=organization,
                status=CHALLENGE_STATUS.COMPLETE,
            )

            challenge_ids = completed_challenges.values_list(
                "pk", flat=True
            )

            try:
                participation = Participation.objects.filter(
                    user=request.user,
                    challenge__pk__in=challenge_ids,
                    status__in=[
                        PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
                        PARTICIPATION_STATUS.ACKNOWLEDGED,
                        PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT
                    ]
                ).latest("pk")

                if not participation:
                    return Response({
                        "message":      _("You don't have Permissions to perform the Action."),
                    }, status=status.HTTP_400_BAD_REQUEST)

            except Participation.DoesNotExist:
                print colored("[--- WARNING ---] Entry does not exist", "yellow")

                return Response({
                    "message":      _("You don't have Permissions to perform the Action."),
                }, status=status.HTTP_400_BAD_REQUEST)

            content_type = ContentType.objects.get_for_model(organization)
            object_id = organization.id

        # ---------------------------------------------------------------------
        # --- Create Complaint
        # ---------------------------------------------------------------------
        complaint = Complaint.objects.create(
            user=request.user,
            text=complaint_text,
            content_type=content_type,
            object_id=object_id,
        )
        complaint.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notifications
        # ---------------------------------------------------------------------
        complaint.email_notify_admins_complaint_created(request)

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="complaint-created",
            message="Complaint was created",
            data={
                "reporter":     request.user.email,
                "object":       complaint.content_object.name,
            },
            # timestamp=timezone.now(),
            targets={
                "reporter":     request.user,
                "object":       complaint.content_object,
            },
            )

        return Response({
            "message":      _("Successfully added the Complaint."),
        }, status=status.HTTP_200_OK)

complaint_list = ComplaintListViewSet.as_view()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ RATINGS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class RatingListViewSet(APIView):
    """Rating List View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = RatingSerializer
    # model = Rating

    def post(self, request):
        """POST: Rating create.

            Receive:

                challenge_id                :uint:
                organization_id             :uint:
                organizer_id                :uint:

                challenge_rating            :int:
                organization_rating         :int:
                organizer_rating            :int:

                challenge_review_text       :str:
                organization_review_text    :str:
                organizer_review_text       :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "challenge_id":                 1,
                    "organization_id":              1,
                    "organizer_id":                 1,
                    "challenge_rating":             5,
                    "organization_rating":          3,
                    "organizer_rating":             4,
                    "challenge_review_text":        "Challenge Review Text",
                    "organization_review_text":     "Organization Review Text",
                    "organizer_review_text":        "Organizer Review Text"
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        challenge_id = request.data.get("challenge_id", "")
        organization_id = request.data.get("organization_id", "")
        organizer_id = request.data.get("organizer_id", "")

        challenge_rating = request.data.get("challenge_rating", "")
        organization_rating = request.data.get("organization_rating", "")
        organizer_rating = request.data.get("organizer_rating", "")

        challenge_review_text = request.data.get("challenge_review_text", "")
        organization_review_text = request.data.get("organization_review_text", "")
        organizer_review_text = request.data.get("organizer_review_text", "")

        print colored("[---  DUMP   ---] CHALLENGE        ID : %s" % challenge_id, "yellow")
        print colored("[---  DUMP   ---] ORGANIZATION     ID : %s" % organization_id, "yellow")
        print colored("[---  DUMP   ---] ORGANIZER        ID : %s" % organizer_id, "yellow")

        print colored("[---  DUMP   ---] CHALLENGE    RATING : %s" % challenge_rating, "yellow")
        print colored("[---  DUMP   ---] ORGANIZATION RATING : %s" % organization_rating, "yellow")
        print colored("[---  DUMP   ---] ORGANIZER    RATING : %s" % organizer_rating, "yellow")

        print colored("[---  DUMP   ---] CHALLENGE    REVIEW : %s" % challenge_review_text, "yellow")
        print colored("[---  DUMP   ---] ORGANIZATION REVIEW : %s" % organization_review_text, "yellow")
        print colored("[---  DUMP   ---] ORGANIZER    REVIEW : %s" % organizer_review_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not challenge_id and not organizer_id:
            return Response({
                "message":      _("Neither Challenge, nor Organizer ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not challenge_rating and not organizer_rating:
            return Response({
                "message":      _("Neither Challenge, nor Organizer Rating provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not challenge_review_text and not organizer_review_text:
            return Response({
                "message":      _("Neither Challenge, nor Organizer Review Text provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if organization_id:
            if not organization_rating:
                return Response({
                    "message":      _("Organization Rating is not provided."),
                }, status=status.HTTP_400_BAD_REQUEST)

            if not organization_review_text:
                return Response({
                    "message":      _("Organization Review Text is not provided."),
                }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve and rate the Challenge
        # ---------------------------------------------------------------------
        if challenge_id:
            challenge = get_object_or_None(
                Challenge,
                id=challenge_id,
            )

            if not challenge:
                return Response({
                    "message":      _("Challenge not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            # -----------------------------------------------------------------
            # --- Check, if the User has already rated the Challenge.
            is_rated = challenge.is_rated_by_user(
                request.user)

            if is_rated:
                return Response({
                    "message":      _("You already rated the Challenge."),
                }, status=status.HTTP_400_BAD_REQUEST)

            # -----------------------------------------------------------------
            # --- Check the Permission
            participation = get_object_or_None(
                Participation,
                user=request.user,
                challenge=challenge,
            )

            if not participation:
                return Response({
                    "message":      _("You don't have Permissions to perform the Action."),
                }, status=status.HTTP_400_BAD_REQUEST)

            if (
                    not participation.is_waiting_for_acknowledgement and
                    not participation.is_acknowledged):
                return Response({
                    "message":      _("You don't have Permissions to perform the Action."),
                }, status=status.HTTP_400_BAD_REQUEST)

            content_type = ContentType.objects.get_for_model(challenge)
            object_id = challenge.id

            rating, created = Rating.objects.get_or_create(
                author=request.user,
                content_type=content_type,
                object_id=object_id,
            )
            rating.rating = int(challenge_rating)
            rating.review_text = challenge_review_text
            rating.save()

        # ---------------------------------------------------------------------
        # --- Retrieve and rate the Organization
        # ---------------------------------------------------------------------
        if organization_id:
            organization = get_object_or_None(
                Organization,
                id=organization_id,
            )

            if not organization:
                return Response({
                    "message":      _("Organization not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            content_type = ContentType.objects.get_for_model(organization)
            object_id = organization.id

            if challenge.organization == organization:
                rating, created = Rating.objects.get_or_create(
                    author=request.user,
                    content_type=content_type,
                    object_id=object_id,
                )
                rating.rating = int(organization_rating)
                rating.review_text = organization_review_text
                rating.save()

        # ---------------------------------------------------------------------
        # --- Retrieve and rate the Organizer
        # ---------------------------------------------------------------------
        if organizer_id:
            organizer = get_object_or_None(
                User,
                id=organizer_id,
            )

            if not organizer:
                return Response({
                    "message":      _("Organizer not found."),
                }, status=status.HTTP_404_NOT_FOUND)

            content_type = ContentType.objects.get_for_model(organizer.profile)
            object_id = organizer.profile.id

            if challenge.author == organizer:
                rating, created = Rating.objects.get_or_create(
                    author=request.user,
                    content_type=content_type,
                    object_id=object_id,
                )
                rating.rating = int(organizer_rating)
                rating.review_text = organizer_review_text
                rating.save()

        return Response({
            "message":      _("Successfully added the Rating."),
        }, status=status.HTTP_200_OK)

rating_list = RatingListViewSet.as_view()


class RatingDetailsViewSet(APIView):
    """Rating Details View Set."""

    authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = RatingSerializer
    # model = Rating

    def delete(self, request, rating_id):
        """DELETE: Rating delete.

            Receive:

                rating_id               :uint:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "rating_id":        100,
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        print colored("[---  DUMP   ---] RATING ID : %s" % rating_id, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not rating_id:
            return Response({
                "message":      _("No Rating ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Rating
        # ---------------------------------------------------------------------
        rating = get_object_or_None(
            Rating,
            pk=rating_id,
        )

        if not rating:
            return Response({
                "message":      _("Rating not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_staff:
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        rating.is_deleted = True
        rating.save()

        return Response({
            "message":      _("Successfully removed the Rating."),
        }, status=status.HTTP_200_OK)

rating_details = RatingDetailsViewSet.as_view()
