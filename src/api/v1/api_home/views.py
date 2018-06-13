import datetime
import inspect
import json

from django.conf import settings
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

from api.auth import CsrfExemptSessionAuthentication
from api.sendgrid_api import send_templated_email
from home.models import FAQ


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ FAQ
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class FAQDetailsViewSet(APIView):
    """FAQ Details View Set."""

    authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = FAQSerializer
    # model = FAQ

    def delete(self, request, faq_id):
        """DELETE: FAQ delete.

            Receive:

                faq_id                  :uint:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "faq_id":           100,
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        print colored("[---  DUMP   ---] FAQ ID : %s" % faq_id, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not faq_id:
            return Response({
                "message":      _("No FAQ ID provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_staff:
            return Response({
                "message":      _("You don't have Permissions to perform the Action."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Retrieve the FAQ
        # ---------------------------------------------------------------------
        faq = get_object_or_None(
            FAQ,
            pk=faq_id,
        )

        if not faq:
            return Response({
                "message":      _("FAQ not found."),
            }, status=status.HTTP_404_NOT_FOUND)

        faq.is_deleted = True
        faq.save()

        return Response({
            "message":      _("Successfully removed the FAQ."),
        }, status=status.HTTP_200_OK)

faq_details = FAQDetailsViewSet.as_view()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ Contact ys
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ContactUsViewSet(APIView):
    """Contact usView Set."""

    # authentication_classes = (CsrfExemptSessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )
    # serializer_class = FAQSerializer
    # model = FAQ

    def post(self, request):
        """POST: Send a Message

            Receive:

                name                    :uint:
                email                   :uint:
                subject                 :uint:
                message                 :uint:

            Return:

                status                  200/400/404/500

            Example Payload:

                {
                    "name":             "Artem Suvorov",
                    "email":            "artem.suvorov@gmail.com",
                    "Subject":          "Question",
                    "Message":          "Some Message",
                }
        """
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        # ---------------------------------------------------------------------
        # --- Retrieve Data from the Request
        # ---------------------------------------------------------------------
        name = request.data.get("name", "")
        email = request.data.get("email", "")
        subject = request.data.get("subject", "")
        message = request.data.get("message", "")

        print colored("[---  DUMP   ---] NAME    : %s" % name, "yellow")
        print colored("[---  DUMP   ---] EMAIL   : %s" % email, "yellow")
        print colored("[---  DUMP   ---] SUBJECT : %s" % subject, "yellow")
        print colored("[---  DUMP   ---] MESSAGE : %s" % message, "yellow")

        # ---------------------------------------------------------------------
        # --- Handle Errors
        # ---------------------------------------------------------------------
        if not name or not email or not subject or not message:
            return Response({
                "message":      _("No Name, Email, Subject or Message provided."),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------------------
        # --- Send the Message
        # ---------------------------------------------------------------------
        if request.user.is_authenticated():
            from_name = "{name} (registered as {account_name} <{account_email}>".format(
                name=name,
                account_name=request.user.get_full_name(),
                account_email=request.user.email,
                )
        else:
            from_name = name

        # --- Send Email
        send_templated_email(
            template_subj={
                "name":     "home/emails/inquiry_subject.txt",
                "context":  {},
            },
            template_text={
                "name":     "home/emails/inquiry.txt",
                "context": {
                    "from_name":        from_name,
                    "from_email":       email,
                    "from_subject":     subject,
                    "from_message":     message,
                },
            },
            template_html=None,
            from_email=settings.EMAIL_SENDER,
            to=[
                settings.EMAIL_SUPPORT,
            ],
            cc=[
                email for admin, email in settings.ADMINS
            ],
            headers=None,
        )

        return Response({
            "message":      _("Successfully sent the Message."),
        }, status=status.HTTP_200_OK)

contact_us = ContactUsViewSet.as_view()
