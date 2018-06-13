import datetime
import inspect
import json

from django.contrib.auth.models import User
from django.contrib.auth.tokens import (
    default_token_generator as token_generator
    )
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.template import loader
from django.utils.http import (
    base36_to_int,
    int_to_base36,
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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ EMAIL
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class EmailUpdateViewSet(APIView):
    """Email Update View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = CommentSerializer
    # model = Comment

    def post(self, request):
        """POST: Email Update.

            Receive:

                email                   :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "email":            "artem.suvorov@gmail.com",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        email = request.data.get("email", "")

        print colored("[---  DUMP   ---] EMAIL : %s" % email, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not email:
            return Response({
                "message":      _("No Email provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- TODO : Validate Email
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # --- Update Email
        # ---------------------------------------------------------------------
        try:
            request.user.email = email
            request.user.save()

            # -----------------------------------------------------------------
            # --- Send Email Notification(s)

        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

            # -----------------------------------------------------------------
            # --- Failed to update the Email
            # --- Save the Log
            papertrail.log(
                event_type="email-update-failed",
                message="email update failed",
                data={
                    "email":    email,
                },
                # timestamp=timezone.now(),
                targets={
                    "user":     request.user,
                },
                )

            return Response({
                "message":      _("Failed to update the Email."),
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message":      _("Successfully updated the Email."),
        }, status=status.HTTP_200_OK)

email_update = EmailUpdateViewSet.as_view()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ PASSWORD
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ForgotPasswordNotifyViewSet(APIView):
    """Forgot Password notify View Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (AllowAny, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = CommentSerializer
    # model = Comment

    def post(self, request):
        """POST: Forgot Password notify.

            Receive:

                email                   :str:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "email":            "artem.suvorov@gmail.com",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        email = request.data.get("email", "")

        print colored("[---  DUMP   ---] EMAIL : %s" % email, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not email:
            return Response({
                "message":      _("No Email provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the User
        # ---------------------------------------------------------------------
        try:
            user = get_object_or_None(
                User,
                email=email,
                )
        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

            return Response({
                "message":      _("Failed to send the Password Renewal Link."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user:
            return Response({
                "message":      _("User not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        print colored("[---  INFO   ---] FOUND USER : %s" % user, "cyan")

        # ---------------------------------------------------------------------
        # --- Send the Password Renewal Link
        # ---------------------------------------------------------------------
        try:
            uidb36 = int_to_base36(user.id)
            token = token_generator.make_token(user)

            DOMAIN_NAME = request.get_host()
            url = reverse(
                "password-renew", kwargs={
                    "uidb36":   uidb36,
                    "token":    token,
                })
            confirmation_link = "http://{domain}{url}".format(
                domain=DOMAIN_NAME,
                url=url,
                )

            # -----------------------------------------------------------------
            # --- Send Email Notification(s)
            user.profile.email_notify_password_reset(
                request=request,
                url=confirmation_link)

        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="exception-forgot-password-notify",
                message="Exception: Forgot Password notify",
                data={
                    "user":     user if user else request.user.email,
                    "message":  str(e),
                },
                # timestamp=timezone.now(),
                targets={
                    "user":     user if user else request.user,
                },
                )

            return Response({
                "message":      _("Failed to send the Password Renewal Link."),
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message":      _("Successfully sent the Password Renewal Link."),
        }, status=status.HTTP_200_OK)

forgot_password_notify = ForgotPasswordNotifyViewSet.as_view()
