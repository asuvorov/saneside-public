import inspect

from termcolor import colored

from easy_pdf.views import PDFTemplateView

from challenges.choices import (
    CHALLENGE_STATUS,
    PARTICIPATION_STATUS,
    )
from challenges.models import Participation


class CompletedChallengesPDF(PDFTemplateView):
    """Export the List of the completed Challenges to PDF."""

    template_name = "accounts/export/my-profile-completed-challenges-export.html"

    def get_context_data(self, **kwargs):
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

        completed_participations = Participation.objects.filter(
            user=self.request.user,
            challenge__status=CHALLENGE_STATUS.COMPLETE,
            status__in=[
                PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
                PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT,
                PARTICIPATION_STATUS.ACKNOWLEDGED,
            ]
        )

        return super(CompletedChallengesPDF, self).get_context_data(
            pagesize="A4",
            title="Hi there!",
            completed_participations=completed_participations,
            **kwargs
        )
