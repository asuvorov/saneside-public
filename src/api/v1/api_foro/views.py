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
from foro.models import (
    Forum,
    Topic,
    Post,
    )


class ForumRemoveViewSet(APIView):
    """Forum remove View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAdminUser, )
    renderer_classes = (JSONRenderer, )
    # serializer_class =ForumSerializer
    # model = Forum

    def post(self, request, forum_id):
        """POST: Forum remove.

            Receive:

                forum_id                :uint:
                cancellation_text       :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "cancellation_text":    "Reason for removal",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        cancellation_text = request.data.get("cancellation_text", "")

        print colored("[---  DUMP   ---] FORUM        ID   : %s" % forum_id, "yellow")
        print colored("[---  DUMP   ---] CANCELLATION TEXT : %s" % cancellation_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not forum_id:
            return Response({
                "message":      _("No Forum ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Forum
        # ---------------------------------------------------------------------
        forum = get_object_or_None(
            Forum,
            id=forum_id,
        )

        if not forum:
            return Response({
                "message":      _("Forum not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        forum.delete()

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # --- Send Notification to the Admin
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="forum-removed",
            message="Forum was removed",
            data={
                "user":     request.user.email,
                "title":    forum.title,
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
            },
            )

        return Response({
            "message":      _("Successfully removed the Forum."),
        }, status=status.HTTP_200_OK)

forum_remove = ForumRemoveViewSet.as_view()


class TopicRemoveViewSet(APIView):
    """Forum Topic remove View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAdminUser, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = TopicSerializer
    # model = Topic

    def post(self, request, topic_id):
        """POST: Forum Topic remove.

            Receive:

                topic_id                :uint:
                cancellation_text       :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "cancellation_text":    "Reason for removal",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        cancellation_text = request.data.get("cancellation_text", "")

        print colored("[---  DUMP   ---] TOPIC        ID   : %s" % topic_id, "yellow")
        print colored("[---  DUMP   ---] CANCELLATION TEXT : %s" % cancellation_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not topic_id:
            return Response({
                "message":      _("No Topic ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Topic
        # ---------------------------------------------------------------------
        topic = get_object_or_None(
            Topic,
            id=topic_id,
        )

        if not topic:
            return Response({
                "message":      _("Topic not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        topic.delete()

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # --- Send Notification to the Admin
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="forum-topic-removed",
            message="Forum Topic was removed",
            data={
                "user":     request.user.email,
                "title":    topic.title,
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
            },
            )

        return Response({
            "message":      _("Successfully removed the Topic."),
        }, status=status.HTTP_200_OK)

topic_remove = TopicRemoveViewSet.as_view()


class PostRemoveViewSet(APIView):
    """Forum Topic Post remove View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAdminUser, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = PostSerializer
    # model = Post

    def post(self, request, post_id):
        """POST: Forum Topic Post remove.

            Receive:

                post_id                 :uint:
                cancellation_text       :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "cancellation_text":    "Reason for removal",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        cancellation_text = request.data.get("cancellation_text", "")

        print colored("[---  DUMP   ---] POST         ID   : %s" % post_id, "yellow")
        print colored("[---  DUMP   ---] CANCELLATION TEXT : %s" % cancellation_text, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not post_id:
            return Response({
                "message":      _("No Post ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Post
        # ---------------------------------------------------------------------
        post = get_object_or_None(
            Post,
            id=post_id,
        )

        if not post:
            return Response({
                "message":      _("Post not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        post.delete()

        # ---------------------------------------------------------------------
        # --- Render HTML Email Content
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # --- Send Notification to the Admin
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="forum-topic-post-removed",
            message="Forum Topic Post was removed",
            data={
                "user":     request.user.email,
                "title":    post.title,
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
            },
            )

        return Response({
            "message":      _("Successfully removed the Post."),
        }, status=status.HTTP_200_OK)

post_remove = PostRemoveViewSet.as_view()
