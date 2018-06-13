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
from blog.choices import POST_STATUS
from blog.models import Post


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ BLOG
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class BlogArchiveViewSet(APIView):
    """Blog Archive View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (AllowAny, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = PostSerializer
    # model = Post

    def get(self, request):
        """GET: Blog Archive.

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
        posts = Post.objects.filter(
            status__in=[
                POST_STATUS.VISIBLE,
            ],
            created__year=year,
            created__month=month,
        )

        for post in posts:
            data.append({
                "date":         post.created.isoformat(),
                "badge":        True,
                "title":        post.title,
                "body":         "",
                "footer":       "",
                "classname":    ""
            })

        return Response({
            "data":     data,
        }, status=status.HTTP_200_OK)

blog_archive = BlogArchiveViewSet.as_view()


class PostPublishViewSet(APIView):
    """Post Publish View Set."""

    permission_classes = (IsAdminUser, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = PostSerializer
    # model = Post

    def post(self, request, post_id):
        """POST: Publish draft Post.

            Receive:

                post_id                 :uint:

            Return:

                status                  200/400/404/500

            Example Payload:

                {}
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        print colored("[---  DUMP   ---] POST ID : %s" % post_id, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not post_id:
            return Response({
                "message":      _("Post ID is not provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Blog Post
        # ---------------------------------------------------------------------
        post = get_object_or_None(
            Post,
            id=post_id,
        )

        if not post:
            return Response({
                "message":      _("Post not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        post.status = POST_STATUS.VISIBLE
        post.save()

        # ---------------------------------------------------------------------
        # --- TODO: Send confirmation Email
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="post-published",
            message="Post was published",
            data={
                "user":     request.user.email,
                "author":   post.author.email,
                "title":    post.title,
                "status":   post.status,
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
                "author":   post.author,
                "post":     post,
            },
            )

        return Response({
            "message":      _("Successfully published the Post."),
        }, status=status.HTTP_200_OK)

post_publish = PostPublishViewSet.as_view()


class PostCloseViewSet(APIView):
    """Post close View Set."""

    permission_classes = (IsAdminUser, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = PostSerializer
    # model = Post

    def post(self, request, post_id):
        """POST: Close the Post.

            Receive:

                post_id                 :uint:

            Return:

                status                  200/400/404/500

            Example Payload:

                {}
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        print colored("[---  DUMP   ---] POST ID : %s" % post_id, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not post_id:
            return Response({
                "message":      _("Post ID is not provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the Blog Post
        # ---------------------------------------------------------------------
        post = get_object_or_None(
            Post,
            id=post_id,
        )

        if not post:
            return Response({
                "message":      _("Post not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        post.status = POST_STATUS.CLOSED
        post.save()

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s)
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # --- Save the Log
        # ---------------------------------------------------------------------
        papertrail.log(
            event_type="post-closed",
            message="Post was closed",
            data={
                "user":     request.user.email,
                "author":   post.author.email,
                "title":    post.title,
                "status":   post.status,
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
                "author":   post.author,
                "post":     post,
            },
            )

        return Response({
            "message":      _("Successfully closed the Post."),
        }, status=status.HTTP_200_OK)

post_close = PostCloseViewSet.as_view()
